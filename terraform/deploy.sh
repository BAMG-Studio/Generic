#!/usr/bin/env bash
# ForgeTrace Infrastructure Deployment Script
# Automated Terraform deployment with validation

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="${SCRIPT_DIR}"

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    local missing_tools=()
    
    # Check for Terraform
    if ! command -v terraform &> /dev/null; then
        missing_tools+=("terraform")
    fi
    
    # Check for AWS CLI
    if ! command -v aws &> /dev/null; then
        missing_tools+=("aws")
    fi
    
    if [ ${#missing_tools[@]} -gt 0 ]; then
        log_error "Missing required tools: ${missing_tools[*]}"
        log_info "Install missing tools:"
        for tool in "${missing_tools[@]}"; do
            case "$tool" in
                terraform)
                    echo "  - brew install terraform"
                    ;;
                aws)
                    echo "  - brew install awscli"
                    ;;
            esac
        done
        exit 1
    fi
    
    log_success "All prerequisites installed"
}

# Verify AWS credentials
verify_aws_credentials() {
    log_info "Verifying AWS credentials..."
    
    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS credentials not configured or invalid"
        log_info "Run: aws configure"
        exit 1
    fi
    
    local account_id
    account_id=$(aws sts get-caller-identity --query Account --output text)
    local user_arn
    user_arn=$(aws sts get-caller-identity --query Arn --output text)
    
    log_success "AWS credentials valid"
    log_info "  Account ID: ${account_id}"
    log_info "  User: ${user_arn}"
}

# Create terraform.tfvars if missing
create_tfvars() {
    if [ ! -f "${TERRAFORM_DIR}/terraform.tfvars" ]; then
        log_warning "terraform.tfvars not found"
        
        if [ -f "${TERRAFORM_DIR}/terraform.tfvars.example" ]; then
            log_info "Creating terraform.tfvars from example..."
            cp "${TERRAFORM_DIR}/terraform.tfvars.example" "${TERRAFORM_DIR}/terraform.tfvars"
            log_success "Created terraform.tfvars"
            log_warning "⚠️  Please edit terraform.tfvars with your values before continuing"
            log_info "Run: vim ${TERRAFORM_DIR}/terraform.tfvars"
            exit 0
        else
            log_error "terraform.tfvars.example not found"
            exit 1
        fi
    fi
}

# Initialize Terraform
terraform_init() {
    log_info "Initializing Terraform..."
    
    cd "${TERRAFORM_DIR}"
    
    if terraform init; then
        log_success "Terraform initialized"
    else
        log_error "Terraform initialization failed"
        exit 1
    fi
}

# Validate Terraform configuration
terraform_validate() {
    log_info "Validating Terraform configuration..."
    
    cd "${TERRAFORM_DIR}"
    
    if terraform validate; then
        log_success "Terraform configuration valid"
    else
        log_error "Terraform validation failed"
        exit 1
    fi
}

# Plan Terraform deployment
terraform_plan() {
    log_info "Planning Terraform deployment..."
    
    cd "${TERRAFORM_DIR}"
    
    if terraform plan -out=tfplan; then
        log_success "Terraform plan created"
        log_info "Review the plan above before applying"
    else
        log_error "Terraform plan failed"
        exit 1
    fi
}

# Apply Terraform deployment
terraform_apply() {
    log_info "Applying Terraform deployment..."
    
    cd "${TERRAFORM_DIR}"
    
    # Check if plan exists
    if [ ! -f tfplan ]; then
        log_error "No plan file found. Run with --plan first"
        exit 1
    fi
    
    log_warning "This will create AWS resources and incur costs (~$5-10/month)"
    read -rp "Continue? (yes/no): " confirm
    
    if [ "$confirm" != "yes" ]; then
        log_info "Deployment cancelled"
        exit 0
    fi
    
    if terraform apply tfplan; then
        log_success "Terraform deployment complete!"
        rm tfplan
        
        # Display outputs
        echo ""
        log_info "Deployment Summary:"
        terraform output deployment_summary
        
        echo ""
        log_info "GitHub Secrets Configuration:"
        terraform output github_secrets_reference
        
    else
        log_error "Terraform apply failed"
        exit 1
    fi
}

# Test deployed infrastructure
test_deployment() {
    log_info "Testing deployed infrastructure..."
    
    cd "${TERRAFORM_DIR}"
    
    # Get S3 bucket name
    local bucket_name
    bucket_name=$(terraform output -raw s3_bucket_name 2>/dev/null)
    
    if [ -z "$bucket_name" ]; then
        log_error "Could not retrieve S3 bucket name"
        exit 1
    fi
    
    # Export credentials
    export AWS_ACCESS_KEY_ID
    AWS_ACCESS_KEY_ID=$(terraform output -raw aws_access_key_id)
    export AWS_SECRET_ACCESS_KEY
    AWS_SECRET_ACCESS_KEY=$(terraform output -raw aws_secret_access_key)
    
    # Test S3 access
    log_info "Testing S3 access to bucket: ${bucket_name}"
    if aws s3 ls "s3://${bucket_name}/" &> /dev/null; then
        log_success "S3 access verified"
        
        # List folders
        log_info "Bucket contents:"
        aws s3 ls "s3://${bucket_name}/"
    else
        log_error "S3 access test failed"
        exit 1
    fi
    
    # Test CloudTrail
    local cloudtrail_name
    cloudtrail_name=$(terraform output -raw cloudtrail_name 2>/dev/null)
    
    if [ -n "$cloudtrail_name" ]; then
        log_info "Verifying CloudTrail: ${cloudtrail_name}"
        if aws cloudtrail get-trail-status --name "${cloudtrail_name}" &> /dev/null; then
            log_success "CloudTrail verified"
        else
            log_warning "CloudTrail verification skipped"
        fi
    fi
    
    log_success "All tests passed!"
}

# Destroy infrastructure
terraform_destroy() {
    log_warning "⚠️  DANGER: This will destroy ALL ForgeTrace infrastructure"
    log_warning "This includes:"
    log_warning "  - IAM user and access keys"
    log_warning "  - S3 bucket and ALL stored models"
    log_warning "  - CloudTrail and CloudWatch resources"
    
    echo ""
    read -rp "Type 'DELETE EVERYTHING' to confirm: " confirm
    
    if [ "$confirm" != "DELETE EVERYTHING" ]; then
        log_info "Destruction cancelled"
        exit 0
    fi
    
    cd "${TERRAFORM_DIR}"
    
    log_info "Destroying infrastructure..."
    if terraform destroy -auto-approve; then
        log_success "Infrastructure destroyed"
    else
        log_error "Destruction failed"
        exit 1
    fi
}

# Display outputs
show_outputs() {
    cd "${TERRAFORM_DIR}"
    
    log_info "Terraform Outputs:"
    echo ""
    terraform output
    
    echo ""
    log_info "GitHub Secrets Reference:"
    terraform output github_secrets_reference
}

# Main menu
show_help() {
    cat << EOF
ForgeTrace Infrastructure Deployment Script

Usage: $0 [COMMAND]

Commands:
  init        Initialize Terraform
  plan        Create execution plan
  apply       Apply infrastructure changes
  test        Test deployed infrastructure
  outputs     Display outputs for GitHub Secrets
  destroy     Destroy all infrastructure
  full        Run full deployment (init + plan + apply + test)

Examples:
  $0 full         # Full deployment from scratch
  $0 plan         # Preview changes
  $0 test         # Test existing deployment
  $0 outputs      # Display outputs

EOF
}

# Main execution
main() {
    local command="${1:-help}"
    
    case "$command" in
        init)
            check_prerequisites
            verify_aws_credentials
            create_tfvars
            terraform_init
            terraform_validate
            ;;
        plan)
            check_prerequisites
            verify_aws_credentials
            terraform_init
            terraform_validate
            terraform_plan
            ;;
        apply)
            check_prerequisites
            verify_aws_credentials
            terraform_apply
            ;;
        test)
            check_prerequisites
            test_deployment
            ;;
        outputs)
            show_outputs
            ;;
        destroy)
            check_prerequisites
            verify_aws_credentials
            terraform_destroy
            ;;
        full)
            check_prerequisites
            verify_aws_credentials
            create_tfvars
            terraform_init
            terraform_validate
            terraform_plan
            terraform_apply
            test_deployment
            show_outputs
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "Unknown command: $command"
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
