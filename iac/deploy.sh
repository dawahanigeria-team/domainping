#!/bin/bash

# DomainPing Infrastructure Deployment Script
# This script automates the deployment of AWS infrastructure using Terraform

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$SCRIPT_DIR/terraform"

# Functions
print_header() {
    echo -e "${BLUE}"
    echo "=================================================="
    echo "🚀 DomainPing Infrastructure Deployment"
    echo "=================================================="
    echo -e "${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

check_prerequisites() {
    print_info "Checking prerequisites..."
    
    # Check if Terraform is installed
    if ! command -v terraform &> /dev/null; then
        print_error "Terraform is not installed. Please install Terraform >= 1.0"
        exit 1
    fi
    
    # Check Terraform version
    TERRAFORM_VERSION=$(terraform version -json | jq -r '.terraform_version')
    print_success "Terraform version: $TERRAFORM_VERSION"
    
    # Check if AWS CLI is installed
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI is not installed. Please install AWS CLI"
        exit 1
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        print_error "AWS credentials not configured. Please run 'aws configure'"
        exit 1
    fi
    
    AWS_ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
    AWS_REGION=$(aws configure get region)
    print_success "AWS Account: $AWS_ACCOUNT"
    print_success "AWS Region: $AWS_REGION"
    
    # Check if jq is installed
    if ! command -v jq &> /dev/null; then
        print_warning "jq is not installed. Some features may not work properly"
    fi
}

setup_terraform() {
    print_info "Setting up Terraform..."
    
    cd "$TERRAFORM_DIR"
    
    # Check if terraform.tfvars exists
    if [ ! -f "terraform.tfvars" ]; then
        print_warning "terraform.tfvars not found. Creating from example..."
        cp terraform.tfvars.example terraform.tfvars
        print_info "Please edit terraform.tfvars with your configuration"
        print_info "File location: $TERRAFORM_DIR/terraform.tfvars"
        
        read -p "Do you want to edit terraform.tfvars now? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            ${EDITOR:-nano} terraform.tfvars
        fi
    fi
    
    # Initialize Terraform
    print_info "Initializing Terraform..."
    terraform init
    
    print_success "Terraform setup complete"
}

plan_deployment() {
    print_info "Planning Terraform deployment..."
    
    cd "$TERRAFORM_DIR"
    
    # Run terraform plan
    terraform plan -out=tfplan
    
    print_success "Terraform plan complete"
    print_info "Plan saved to: $TERRAFORM_DIR/tfplan"
}

deploy_infrastructure() {
    print_info "Deploying infrastructure..."
    
    cd "$TERRAFORM_DIR"
    
    # Apply the plan
    terraform apply tfplan
    
    print_success "Infrastructure deployment complete!"
}

show_outputs() {
    print_info "Deployment outputs:"
    
    cd "$TERRAFORM_DIR"
    
    echo -e "${GREEN}"
    terraform output
    echo -e "${NC}"
    
    # Get key values for GitHub Actions
    print_info "GitHub Actions Configuration:"
    echo "Add these secrets to your GitHub repository:"
    echo
    
    if command -v jq &> /dev/null; then
        AWS_ACCESS_KEY_ID=$(terraform output -raw github_actions_access_key_id 2>/dev/null || echo "N/A")
        AWS_SECRET_ACCESS_KEY=$(terraform output -raw github_actions_secret_access_key 2>/dev/null || echo "N/A")
        AWS_S3_BUCKET=$(terraform output -raw s3_bucket_name 2>/dev/null || echo "N/A")
        CLOUDFRONT_DISTRIBUTION_ID=$(terraform output -raw cloudfront_distribution_id 2>/dev/null || echo "N/A")
        AWS_REGION=$(terraform output -raw aws_region 2>/dev/null || echo "us-east-1")
        WEBSITE_URL=$(terraform output -raw website_url 2>/dev/null || echo "N/A")
        
        echo "AWS_ACCESS_KEY_ID: $AWS_ACCESS_KEY_ID"
        echo "AWS_SECRET_ACCESS_KEY: [SENSITIVE - use terraform output]"
        echo "AWS_S3_BUCKET: $AWS_S3_BUCKET"
        echo "CLOUDFRONT_DISTRIBUTION_ID: $CLOUDFRONT_DISTRIBUTION_ID"
        echo "AWS_REGION: $AWS_REGION"
        echo
        print_success "Website URL: $WEBSITE_URL"
    else
        print_warning "Install jq for formatted output"
    fi
}

setup_github_secrets() {
    print_info "Setting up GitHub secrets..."
    
    if ! command -v gh &> /dev/null; then
        print_warning "GitHub CLI not installed. Please install 'gh' to automatically set secrets"
        print_info "Or manually add the secrets shown above to your GitHub repository"
        return
    fi
    
    cd "$TERRAFORM_DIR"
    
    read -p "Do you want to automatically set GitHub secrets? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Setting GitHub secrets..."
        
        AWS_ACCESS_KEY_ID=$(terraform output -raw github_actions_access_key_id)
        AWS_SECRET_ACCESS_KEY=$(terraform output -raw github_actions_secret_access_key)
        AWS_S3_BUCKET=$(terraform output -raw s3_bucket_name)
        CLOUDFRONT_DISTRIBUTION_ID=$(terraform output -raw cloudfront_distribution_id)
        AWS_REGION=$(terraform output -raw aws_region)
        
        gh secret set AWS_ACCESS_KEY_ID --body "$AWS_ACCESS_KEY_ID"
        gh secret set AWS_SECRET_ACCESS_KEY --body "$AWS_SECRET_ACCESS_KEY"
        gh secret set AWS_S3_BUCKET --body "$AWS_S3_BUCKET"
        gh secret set CLOUDFRONT_DISTRIBUTION_ID --body "$CLOUDFRONT_DISTRIBUTION_ID"
        gh secret set AWS_REGION --body "$AWS_REGION"
        
        print_success "GitHub secrets configured!"
    fi
}

cleanup() {
    cd "$TERRAFORM_DIR"
    if [ -f "tfplan" ]; then
        rm tfplan
        print_info "Cleaned up temporary files"
    fi
}

show_help() {
    echo "DomainPing Infrastructure Deployment Script"
    echo
    echo "Usage: $0 [COMMAND]"
    echo
    echo "Commands:"
    echo "  deploy    - Full deployment (plan + apply)"
    echo "  plan      - Plan deployment only"
    echo "  apply     - Apply existing plan"
    echo "  output    - Show deployment outputs"
    echo "  destroy   - Destroy infrastructure"
    echo "  help      - Show this help"
    echo
    echo "Examples:"
    echo "  $0 deploy    # Full deployment"
    echo "  $0 plan      # Plan only"
    echo "  $0 output    # Show outputs"
}

destroy_infrastructure() {
    print_warning "This will destroy ALL infrastructure resources!"
    print_warning "This action cannot be undone!"
    echo
    
    read -p "Are you sure you want to destroy the infrastructure? (type 'yes' to confirm): " -r
    if [[ $REPLY == "yes" ]]; then
        cd "$TERRAFORM_DIR"
        terraform destroy
        print_success "Infrastructure destroyed"
    else
        print_info "Destruction cancelled"
    fi
}

# Main script
main() {
    print_header
    
    case "${1:-deploy}" in
        "deploy")
            check_prerequisites
            setup_terraform
            plan_deployment
            deploy_infrastructure
            show_outputs
            setup_github_secrets
            cleanup
            ;;
        "plan")
            check_prerequisites
            setup_terraform
            plan_deployment
            ;;
        "apply")
            check_prerequisites
            cd "$TERRAFORM_DIR"
            if [ ! -f "tfplan" ]; then
                print_error "No plan file found. Run 'plan' first or use 'deploy'"
                exit 1
            fi
            deploy_infrastructure
            show_outputs
            setup_github_secrets
            cleanup
            ;;
        "output")
            cd "$TERRAFORM_DIR"
            show_outputs
            ;;
        "destroy")
            check_prerequisites
            destroy_infrastructure
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            print_error "Unknown command: $1"
            show_help
            exit 1
            ;;
    esac
}

# Trap to cleanup on exit
trap cleanup EXIT

# Run main function
main "$@" 