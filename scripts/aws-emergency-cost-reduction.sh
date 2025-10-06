#!/bin/bash
# AWS Emergency Cost Reduction Script
# This script will delete ALL costly AWS resources to reduce to free tier only
# WARNING: This will PERMANENTLY DELETE resources. Review carefully before running.

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Function to check if AWS CLI is configured
check_aws_cli() {
    if ! command -v aws &> /dev/null; then
        error "AWS CLI not found. Please install AWS CLI first."
        exit 1
    fi
    
    if ! aws sts get-caller-identity &> /dev/null; then
        error "AWS CLI not configured or no valid credentials. Please run 'aws configure'."
        exit 1
    fi
}

# Function to get all AWS regions
get_regions() {
    aws ec2 describe-regions --query 'Regions[].RegionName' --output text
}

# Function to delete EKS clusters (Elastic Container Service for Kubernetes)
delete_eks_clusters() {
    log "Deleting EKS clusters..."
    
    for region in $(get_regions); do
        log "Checking region: $region"
        
        # Get EKS clusters
        clusters=$(aws eks list-clusters --region $region --query 'clusters[]' --output text 2>/dev/null || echo "")
        
        for cluster in $clusters; do
            if [ ! -z "$cluster" ]; then
                warning "Deleting EKS cluster: $cluster in $region"
                
                # Delete nodegroups first
                nodegroups=$(aws eks list-nodegroups --cluster-name $cluster --region $region --query 'nodegroups[]' --output text 2>/dev/null || echo "")
                for nodegroup in $nodegroups; do
                    if [ ! -z "$nodegroup" ]; then
                        log "Deleting nodegroup: $nodegroup"
                        aws eks delete-nodegroup --cluster-name $cluster --nodegroup-name $nodegroup --region $region
                        # Wait for nodegroup deletion
                        aws eks wait nodegroup-deleted --cluster-name $cluster --nodegroup-name $nodegroup --region $region
                    fi
                done
                
                # Delete cluster
                aws eks delete-cluster --name $cluster --region $region
                success "EKS cluster $cluster deletion initiated in $region"
            fi
        done
    done
}

# Function to delete EC2 instances
delete_ec2_instances() {
    log "Terminating EC2 instances..."
    
    for region in $(get_regions); do
        log "Checking region: $region"
        
        # Get running instances
        instances=$(aws ec2 describe-instances --region $region \
            --filters "Name=instance-state-name,Values=running,stopped" \
            --query 'Reservations[].Instances[].InstanceId' --output text 2>/dev/null || echo "")
        
        if [ ! -z "$instances" ]; then
            warning "Terminating EC2 instances in $region: $instances"
            aws ec2 terminate-instances --instance-ids $instances --region $region
            success "EC2 instances termination initiated in $region"
        fi
    done
}

# Function to delete EBS volumes
delete_ebs_volumes() {
    log "Deleting EBS volumes..."
    
    for region in $(get_regions); do
        log "Checking region: $region"
        
        # Get available (unattached) volumes
        volumes=$(aws ec2 describe-volumes --region $region \
            --filters "Name=status,Values=available" \
            --query 'Volumes[].VolumeId' --output text 2>/dev/null || echo "")
        
        for volume in $volumes; do
            if [ ! -z "$volume" ]; then
                warning "Deleting EBS volume: $volume in $region"
                aws ec2 delete-volume --volume-id $volume --region $region
                success "EBS volume $volume deleted in $region"
            fi
        done
    done
}

# Function to delete VPCs (keeping default VPC)
delete_custom_vpcs() {
    log "Deleting custom VPCs..."
    
    for region in $(get_regions); do
        log "Checking region: $region"
        
        # Get non-default VPCs
        vpcs=$(aws ec2 describe-vpcs --region $region \
            --filters "Name=is-default,Values=false" \
            --query 'Vpcs[].VpcId' --output text 2>/dev/null || echo "")
        
        for vpc in $vpcs; do
            if [ ! -z "$vpc" ]; then
                warning "Deleting custom VPC: $vpc in $region"
                
                # Delete VPC dependencies first
                # Delete NAT gateways
                nat_gateways=$(aws ec2 describe-nat-gateways --region $region \
                    --filter "Name=vpc-id,Values=$vpc" \
                    --query 'NatGateways[?State==`available`].NatGatewayId' --output text 2>/dev/null || echo "")
                
                for nat_gw in $nat_gateways; do
                    if [ ! -z "$nat_gw" ]; then
                        log "Deleting NAT Gateway: $nat_gw"
                        aws ec2 delete-nat-gateway --nat-gateway-id $nat_gw --region $region
                    fi
                done
                
                # Delete internet gateways
                igws=$(aws ec2 describe-internet-gateways --region $region \
                    --filters "Name=attachment.vpc-id,Values=$vpc" \
                    --query 'InternetGateways[].InternetGatewayId' --output text 2>/dev/null || echo "")
                
                for igw in $igws; do
                    if [ ! -z "$igw" ]; then
                        log "Detaching and deleting Internet Gateway: $igw"
                        aws ec2 detach-internet-gateway --internet-gateway-id $igw --vpc-id $vpc --region $region
                        aws ec2 delete-internet-gateway --internet-gateway-id $igw --region $region
                    fi
                done
                
                # Delete subnets
                subnets=$(aws ec2 describe-subnets --region $region \
                    --filters "Name=vpc-id,Values=$vpc" \
                    --query 'Subnets[].SubnetId' --output text 2>/dev/null || echo "")
                
                for subnet in $subnets; do
                    if [ ! -z "$subnet" ]; then
                        log "Deleting subnet: $subnet"
                        aws ec2 delete-subnet --subnet-id $subnet --region $region
                    fi
                done
                
                # Delete security groups (except default)
                security_groups=$(aws ec2 describe-security-groups --region $region \
                    --filters "Name=vpc-id,Values=$vpc" "Name=group-name,Values=*" \
                    --query 'SecurityGroups[?GroupName!=`default`].GroupId' --output text 2>/dev/null || echo "")
                
                for sg in $security_groups; do
                    if [ ! -z "$sg" ]; then
                        log "Deleting security group: $sg"
                        aws ec2 delete-security-group --group-id $sg --region $region 2>/dev/null || true
                    fi
                done
                
                # Finally delete the VPC
                aws ec2 delete-vpc --vpc-id $vpc --region $region
                success "VPC $vpc deleted in $region"
            fi
        done
    done
}

# Function to disable Security Hub
disable_security_hub() {
    log "Disabling Security Hub..."
    
    for region in $(get_regions); do
        log "Checking Security Hub in region: $region"
        
        # Check if Security Hub is enabled
        if aws securityhub get-enabled-standards --region $region &>/dev/null; then
            warning "Disabling Security Hub in $region"
            
            # Disable all standards first
            standards=$(aws securityhub get-enabled-standards --region $region \
                --query 'StandardsSubscriptions[].StandardsSubscriptionArn' --output text 2>/dev/null || echo "")
            
            for standard in $standards; do
                if [ ! -z "$standard" ]; then
                    log "Disabling standard: $standard"
                    aws securityhub batch-disable-standards --standards-subscription-arns $standard --region $region
                fi
            done
            
            # Disable Security Hub
            aws securityhub disable-security-hub --region $region
            success "Security Hub disabled in $region"
        fi
    done
}

# Function to delete KMS keys (customer managed only)
delete_kms_keys() {
    log "Scheduling deletion of customer-managed KMS keys..."
    
    for region in $(get_regions); do
        log "Checking KMS keys in region: $region"
        
        # Get customer-managed keys
        keys=$(aws kms list-keys --region $region --query 'Keys[].KeyId' --output text 2>/dev/null || echo "")
        
        for key in $keys; do
            if [ ! -z "$key" ]; then
                # Check if it's customer managed
                key_info=$(aws kms describe-key --key-id $key --region $region 2>/dev/null || echo "")
                if echo "$key_info" | grep -q '"KeyManager": "CUSTOMER"'; then
                    warning "Scheduling deletion of KMS key: $key in $region"
                    aws kms schedule-key-deletion --key-id $key --pending-window-in-days 7 --region $region
                    success "KMS key $key scheduled for deletion in $region"
                fi
            fi
        done
    done
}

# Function to delete CloudWatch resources
cleanup_cloudwatch() {
    log "Cleaning up CloudWatch resources..."
    
    for region in $(get_regions); do
        log "Checking CloudWatch in region: $region"
        
        # Delete custom metrics alarms
        alarms=$(aws cloudwatch describe-alarms --region $region \
            --query 'MetricAlarms[].AlarmName' --output text 2>/dev/null || echo "")
        
        for alarm in $alarms; do
            if [ ! -z "$alarm" ]; then
                log "Deleting CloudWatch alarm: $alarm"
                aws cloudwatch delete-alarms --alarm-names $alarm --region $region
            fi
        done
        
        # Delete log groups (keep /aws/lambda and /aws/apigateway for free tier)
        log_groups=$(aws logs describe-log-groups --region $region \
            --query 'logGroups[?!starts_with(logGroupName, `/aws/lambda`) && !starts_with(logGroupName, `/aws/apigateway`)].logGroupName' --output text 2>/dev/null || echo "")
        
        for log_group in $log_groups; do
            if [ ! -z "$log_group" ]; then
                warning "Deleting log group: $log_group"
                aws logs delete-log-group --log-group-name "$log_group" --region $region
            fi
        done
        
        success "CloudWatch cleanup completed in $region"
    done
}

# Function to delete ECR repositories
delete_ecr_repositories() {
    log "Deleting ECR repositories..."
    
    for region in $(get_regions); do
        log "Checking ECR repositories in region: $region"
        
        repositories=$(aws ecr describe-repositories --region $region \
            --query 'repositories[].repositoryName' --output text 2>/dev/null || echo "")
        
        for repo in $repositories; do
            if [ ! -z "$repo" ]; then
                warning "Deleting ECR repository: $repo in $region"
                aws ecr delete-repository --repository-name $repo --force --region $region
                success "ECR repository $repo deleted in $region"
            fi
        done
    done
}

# Function to delete Load Balancers
delete_load_balancers() {
    log "Deleting Load Balancers..."
    
    for region in $(get_regions); do
        log "Checking Load Balancers in region: $region"
        
        # Delete Application Load Balancers
        albs=$(aws elbv2 describe-load-balancers --region $region \
            --query 'LoadBalancers[].LoadBalancerArn' --output text 2>/dev/null || echo "")
        
        for alb in $albs; do
            if [ ! -z "$alb" ]; then
                warning "Deleting ALB: $alb"
                aws elbv2 delete-load-balancer --load-balancer-arn $alb --region $region
            fi
        done
        
        # Delete Classic Load Balancers
        clbs=$(aws elb describe-load-balancers --region $region \
            --query 'LoadBalancerDescriptions[].LoadBalancerName' --output text 2>/dev/null || echo "")
        
        for clb in $clbs; do
            if [ ! -z "$clb" ]; then
                warning "Deleting CLB: $clb"
                aws elb delete-load-balancer --load-balancer-name $clb --region $region
            fi
        done
    done
}

# Function to release Elastic IPs
release_elastic_ips() {
    log "Releasing Elastic IPs..."
    
    for region in $(get_regions); do
        log "Checking Elastic IPs in region: $region"
        
        eips=$(aws ec2 describe-addresses --region $region \
            --query 'Addresses[?!InstanceId].AllocationId' --output text 2>/dev/null || echo "")
        
        for eip in $eips; do
            if [ ! -z "$eip" ]; then
                warning "Releasing Elastic IP: $eip in $region"
                aws ec2 release-address --allocation-id $eip --region $region
                success "Elastic IP $eip released in $region"
            fi
        done
    done
}

# Main execution function
main() {
    log "Starting AWS Emergency Cost Reduction"
    log "This will DELETE ALL costly AWS resources!"
    
    echo -e "${RED}"
    cat << 'EOF'
╔══════════════════════════════════════════════════════════════════════════════╗
║                                 WARNING                                      ║
║                                                                              ║
║  This script will PERMANENTLY DELETE the following AWS resources:           ║
║  • All EKS clusters and node groups                                         ║
║  • All EC2 instances                                                        ║
║  • All unattached EBS volumes                                               ║
║  • All custom VPCs (keeping default VPCs)                                   ║
║  • Security Hub (disable)                                                   ║
║  • Customer-managed KMS keys (scheduled deletion)                           ║
║  • CloudWatch alarms and custom log groups                                  ║
║  • ECR repositories                                                         ║
║  • Load Balancers                                                           ║
║  • Unattached Elastic IPs                                                   ║
║                                                                              ║
║  This action is IRREVERSIBLE and will result in DATA LOSS!                 ║
║                                                                              ║
╚═══════════════════════════════���══════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
    
    read -p "Are you ABSOLUTELY SURE you want to proceed? Type 'DELETE-ALL-RESOURCES' to continue: " confirmation
    
    if [ "$confirmation" != "DELETE-ALL-RESOURCES" ]; then
        log "Operation cancelled by user"
        exit 0
    fi
    
    check_aws_cli
    
    log "Proceeding with resource deletion..."
    
    # Execute cleanup functions
    delete_eks_clusters
    delete_ec2_instances
    sleep 10  # Wait a bit before cleaning volumes
    delete_ebs_volumes
    delete_load_balancers
    release_elastic_ips
    delete_ecr_repositories
    cleanup_cloudwatch
    disable_security_hub
    delete_kms_keys
    delete_custom_vpcs
    
    success "AWS Emergency Cost Reduction completed!"
    
    log "Summary of actions taken:"
    log "✅ EKS clusters deleted"
    log "✅ EC2 instances terminated"
    log "✅ EBS volumes deleted"
    log "✅ Load Balancers deleted"
    log "✅ Elastic IPs released"
    log "✅ ECR repositories deleted"
    log "✅ CloudWatch resources cleaned"
    log "✅ Security Hub disabled"
    log "✅ KMS keys scheduled for deletion"
    log "✅ Custom VPCs deleted"
    
    warning "Note: Some resources may take time to fully terminate."
    warning "KMS keys will be deleted in 7 days (minimum waiting period)."
    log "Your AWS costs should now be reduced to free-tier levels."
    
    log "Recommended next steps:"
    log "1. Monitor AWS billing for 24-48 hours to confirm cost reduction"
    log "2. Set up billing alerts for future cost monitoring"
    log "3. Use AWS Free Tier resources only for development"
}

# Run the main function
main "$@"