#!/bin/bash
# Terraform Infrastructure Destruction Script
# Safely destroys all Terraform-managed AWS resources

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# Function to destroy Terraform resources
destroy_terraform_infrastructure() {
    local terraform_dir="$1"
    
    if [ ! -d "$terraform_dir" ]; then
        warning "Directory $terraform_dir does not exist, skipping..."
        return 0
    fi
    
    log "Destroying Terraform infrastructure in: $terraform_dir"
    
    cd "$terraform_dir"
    
    # Check if Terraform files exist
    if ! ls *.tf &> /dev/null; then
        warning "No Terraform files found in $terraform_dir"
        return 0
    fi
    
    # Initialize Terraform
    log "Initializing Terraform..."
    if ! terraform init; then
        error "Failed to initialize Terraform in $terraform_dir"
        return 1
    fi
    
    # Plan destroy
    log "Planning destruction..."
    if ! terraform plan -destroy -out=destroy.tfplan; then
        error "Failed to create destroy plan in $terraform_dir"
        return 1
    fi
    
    # Apply destroy
    warning "Destroying infrastructure in $terraform_dir"
    if terraform apply destroy.tfplan; then
        success "Successfully destroyed infrastructure in $terraform_dir"
        rm -f destroy.tfplan
    else
        error "Failed to destroy infrastructure in $terraform_dir"
        return 1
    fi
}

main() {
    local base_dir="/home/papaert/projects/lab"
    
    log "Starting Terraform infrastructure destruction"
    
    echo -e "${RED}"
    cat << 'EOF'
╔══════════════════════════════════════════════════════════════════════════════╗
║                           TERRAFORM DESTROY WARNING                          ║
║                                                                              ║
║  This script will DESTROY all Terraform-managed infrastructure including:   ║
║  • OIDC providers                                                           ║
║  • IAM roles and policies                                                   ║
║  • S3 buckets                                                               ║
║  • DynamoDB tables                                                          ║
║  • Any other Terraform-managed resources                                    ║
║                                                                              ║
║  This action is IRREVERSIBLE!                                              ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
    
    read -p "Are you sure you want to destroy all Terraform infrastructure? Type 'DESTROY' to continue: " confirmation
    
    if [ "$confirmation" != "DESTROY" ]; then
        log "Operation cancelled by user"
        exit 0
    fi
    
    # List of Terraform directories to destroy
    terraform_dirs=(
        "$base_dir"
        "$base_dir/solutions/scenario-s003-000-secure-cicd-gha/iac/terraform"
        "$base_dir/solutions/demo-sbom-lab/terraform"
        "$base_dir/modules/oidc-github"
    )
    
    # Destroy each Terraform directory
    for dir in "${terraform_dirs[@]}"; do
        if [ -d "$dir" ]; then
            destroy_terraform_infrastructure "$dir"
        else
            warning "Directory $dir does not exist, skipping..."
        fi
    done
    
    # Clean up Terraform state files
    log "Cleaning up Terraform state files..."
    find "$base_dir" -name "terraform.tfstate*" -type f -exec rm -f {} \;
    find "$base_dir" -name ".terraform" -type d -exec rm -rf {} \; 2>/dev/null || true
    find "$base_dir" -name "*.tfplan" -type f -exec rm -f {} \;
    
    success "Terraform infrastructure destruction completed!"
    
    log "Next steps:"
    log "1. Run the AWS emergency cost reduction script"
    log "2. Verify all resources are deleted in AWS Console"
    log "3. Monitor billing for 24-48 hours"
}

main "$@"