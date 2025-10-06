#!/bin/bash
# Master AWS Cost Reduction Script
# Orchestrates complete cost reduction to free tier

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

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

# Function to check current AWS costs
check_current_costs() {
    log "Checking current AWS costs..."
    
    # Get current month costs
    local start_date=$(date -d "$(date +%Y-%m-01)" '+%Y-%m-%d')
    local end_date=$(date '+%Y-%m-%d')
    
    aws ce get-cost-and-usage \
        --time-period Start=$start_date,End=$end_date \
        --granularity MONTHLY \
        --metrics BlendedCost \
        --query 'ResultsByTime[0].Total.BlendedCost.Amount' \
        --output text > /tmp/current_cost.txt
    
    local current_cost=$(cat /tmp/current_cost.txt)
    log "Current month-to-date cost: \$${current_cost}"
    
    rm -f /tmp/current_cost.txt
    return 0
}

# Function to list all resources across regions
audit_resources() {
    log "Auditing AWS resources across all regions..."
    
    local audit_file="/tmp/aws_resource_audit_$(date +%Y%m%d_%H%M%S).txt"
    
    echo "AWS Resource Audit - $(date)" > "$audit_file"
    echo "===========================================" >> "$audit_file"
    
    for region in $(aws ec2 describe-regions --query 'Regions[].RegionName' --output text); do
        echo "" >> "$audit_file"
        echo "Region: $region" >> "$audit_file"
        echo "-------------------" >> "$audit_file"
        
        # EC2 instances
        local instances=$(aws ec2 describe-instances --region $region \
            --query 'Reservations[*].Instances[*].[InstanceId,InstanceType,State.Name,LaunchTime]' \
            --output text 2>/dev/null | wc -l)
        echo "EC2 Instances: $instances" >> "$audit_file"
        
        # EKS clusters
        local eks_clusters=$(aws eks list-clusters --region $region \
            --query 'length(clusters)' --output text 2>/dev/null || echo "0")
        echo "EKS Clusters: $eks_clusters" >> "$audit_file"
        
        # Load Balancers
        local albs=$(aws elbv2 describe-load-balancers --region $region \
            --query 'length(LoadBalancers)' --output text 2>/dev/null || echo "0")
        echo "Application Load Balancers: $albs" >> "$audit_file"
        
        # RDS instances
        local rds=$(aws rds describe-db-instances --region $region \
            --query 'length(DBInstances)' --output text 2>/dev/null || echo "0")
        echo "RDS Instances: $rds" >> "$audit_file"
        
        # NAT Gateways
        local nat_gws=$(aws ec2 describe-nat-gateways --region $region \
            --query 'length(NatGateways)' --output text 2>/dev/null || echo "0")
        echo "NAT Gateways: $nat_gws" >> "$audit_file"
    done
    
    success "Resource audit completed: $audit_file"
    cat "$audit_file"
}

# Function to estimate cost savings
estimate_savings() {
    log "Estimating potential cost savings..."
    
    cat << 'EOF'
Estimated Monthly Cost Savings:
===============================

Based on your current usage ($286.96 total):

• EKS Clusters: ~$178.91 (62.3%)
• EC2 Instances: ~$35.83 (12.5%)
• Tax: ~$15.59 (5.4%)
• VPC (NAT Gateway): ~$15.41 (5.4%)
• Security Hub: ~$3.81 (1.3%)
• KMS: ~$1.41 (0.5%)
• Config: ~$0.60 (0.2%)

Total Estimated Savings: $251.56 (87.6%)
Remaining Free Tier Cost: ~$35.40 (12.4%)

Note: Costs may vary based on actual usage patterns.
EOF
}

main() {
    log "AWS Master Cost Reduction Script"
    
    echo -e "${RED}"
    cat << 'EOF'
╔══════════════════════════════════════════════════════════════════════════════╗
║                     MASTER AWS COST REDUCTION SCRIPT                        ║
║                                                                              ║
║  This script will execute a complete cost reduction process:                 ║
║                                                                              ║
║  Phase 1: Audit current resources and costs                                 ║
║  Phase 2: Destroy Terraform-managed infrastructure                          ║
║  Phase 3: Delete all costly AWS resources                                   ║
║  Phase 4: Set up cost monitoring and protection                             ║
║                                                                              ║
║  Expected result: Reduce costs from $286.96 to ~$35 (87.6% reduction)      ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
    
    echo "Choose your action:"
    echo "1. Full cost reduction (all phases)"
    echo "2. Audit only (check current resources)"
    echo "3. Terraform destroy only"
    echo "4. AWS resource cleanup only" 
    echo "5. Set up cost protection only"
    echo "6. Exit"
    
    read -p "Enter your choice (1-6): " choice
    
    case $choice in
        1)
            log "Executing full cost reduction process..."
            
            # Phase 1: Audit
            log "=== PHASE 1: AUDIT ==="
            check_current_costs
            audit_resources
            estimate_savings
            
            echo ""
            read -p "Continue with destruction? This will DELETE resources! (type 'YES' to continue): " confirm
            if [ "$confirm" != "YES" ]; then
                log "Operation cancelled"
                exit 0
            fi
            
            # Phase 2: Terraform destroy
            log "=== PHASE 2: TERRAFORM DESTROY ==="
            if [ -f "$SCRIPT_DIR/terraform-destroy-all.sh" ]; then
                "$SCRIPT_DIR/terraform-destroy-all.sh"
            else
                warning "Terraform destroy script not found"
            fi
            
            # Phase 3: AWS resource cleanup
            log "=== PHASE 3: AWS RESOURCE CLEANUP ==="
            if [ -f "$SCRIPT_DIR/aws-emergency-cost-reduction.sh" ]; then
                "$SCRIPT_DIR/aws-emergency-cost-reduction.sh"
            else
                error "AWS emergency cost reduction script not found"
                exit 1
            fi
            
            # Phase 4: Cost protection
            log "=== PHASE 4: COST PROTECTION SETUP ==="
            if [ -f "$SCRIPT_DIR/aws-free-tier-protection.sh" ]; then
                "$SCRIPT_DIR/aws-free-tier-protection.sh"
            else
                warning "Cost protection script not found"
            fi
            
            success "Full cost reduction process completed!"
            ;;
            
        2)
            log "=== AUDIT ONLY ==="
            check_current_costs
            audit_resources
            estimate_savings
            ;;
            
        3)
            log "=== TERRAFORM DESTROY ONLY ==="
            if [ -f "$SCRIPT_DIR/terraform-destroy-all.sh" ]; then
                "$SCRIPT_DIR/terraform-destroy-all.sh"
            else
                error "Terraform destroy script not found"
                exit 1
            fi
            ;;
            
        4)
            log "=== AWS RESOURCE CLEANUP ONLY ==="
            if [ -f "$SCRIPT_DIR/aws-emergency-cost-reduction.sh" ]; then
                "$SCRIPT_DIR/aws-emergency-cost-reduction.sh"
            else
                error "AWS emergency cost reduction script not found"
                exit 1
            fi
            ;;
            
        5)
            log "=== COST PROTECTION SETUP ONLY ==="
            if [ -f "$SCRIPT_DIR/aws-free-tier-protection.sh" ]; then
                "$SCRIPT_DIR/aws-free-tier-protection.sh"
            else
                error "Cost protection script not found"
                exit 1
            fi
            ;;
            
        6)
            log "Exiting..."
            exit 0
            ;;
            
        *)
            error "Invalid choice. Exiting..."
            exit 1
            ;;
    esac
    
    log "Operation completed. Check AWS Console to verify changes."
    log "Monitor your billing dashboard for the next 24-48 hours."
}

# Check if AWS CLI is available
if ! command -v aws &> /dev/null; then
    error "AWS CLI not found. Please install AWS CLI first."
    exit 1
fi

# Check if AWS CLI is configured
if ! aws sts get-caller-identity &> /dev/null; then
    error "AWS CLI not configured. Please run 'aws configure' first."
    exit 1
fi

main "$@"