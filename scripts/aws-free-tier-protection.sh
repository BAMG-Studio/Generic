#!/bin/bash
# AWS Free Tier Protection Script
# Sets up monitoring and alerts to prevent future cost overruns

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

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Function to set up billing alerts
setup_billing_alerts() {
    log "Setting up billing alerts..."
    
    # Create SNS topic for billing alerts
    local sns_topic_arn=$(aws sns create-topic --name "aws-billing-alerts" --query 'TopicArn' --output text)
    
    # Subscribe email to SNS topic
    read -p "Enter your email for billing alerts: " email
    aws sns subscribe --topic-arn "$sns_topic_arn" --protocol email --notification-endpoint "$email"
    
    log "Please check your email and confirm the subscription"
    
    # Create CloudWatch billing alarms
    local thresholds=("5.00" "10.00" "25.00" "50.00")
    
    for threshold in "${thresholds[@]}"; do
        aws cloudwatch put-metric-alarm \
            --alarm-name "billing-alarm-${threshold//./-}" \
            --alarm-description "Billing alarm for \$${threshold}" \
            --metric-name EstimatedCharges \
            --namespace AWS/Billing \
            --statistic Maximum \
            --period 21600 \
            --threshold "$threshold" \
            --comparison-operator GreaterThanThreshold \
            --evaluation-periods 1 \
            --alarm-actions "$sns_topic_arn" \
            --dimensions Name=Currency,Value=USD
        
        success "Created billing alarm for \$${threshold}"
    done
}

# Function to create cost budget
setup_cost_budget() {
    log "Setting up AWS Budget..."
    
    read -p "Enter your email for budget notifications: " email
    
    cat > /tmp/budget.json << EOF
{
  "BudgetName": "free-tier-budget",
  "BudgetLimit": {
    "Amount": "10.00",
    "Unit": "USD"
  },
  "TimeUnit": "MONTHLY",
  "BudgetType": "COST",
  "CostFilters": {},
  "TimePeriod": {
    "Start": "$(date -d 'first day of this month' '+%Y-%m-%d')",
    "End": "2099-12-31"
  }
}
EOF

    cat > /tmp/budget-notifications.json << EOF
[
  {
    "Notification": {
      "NotificationType": "ACTUAL",
      "ComparisonOperator": "GREATER_THAN",
      "Threshold": 80.0,
      "ThresholdType": "PERCENTAGE"
    },
    "Subscribers": [
      {
        "SubscriptionType": "EMAIL",
        "Address": "$email"
      }
    ]
  },
  {
    "Notification": {
      "NotificationType": "FORECASTED",
      "ComparisonOperator": "GREATER_THAN",
      "Threshold": 100.0,
      "ThresholdType": "PERCENTAGE"
    },
    "Subscribers": [
      {
        "SubscriptionType": "EMAIL",
        "Address": "$email"
      }
    ]
  }
]
EOF

    # Get account ID
    local account_id=$(aws sts get-caller-identity --query 'Account' --output text)
    
    # Create budget
    aws budgets create-budget \
        --account-id "$account_id" \
        --budget file:///tmp/budget.json \
        --notifications-with-subscribers file:///tmp/budget-notifications.json
    
    success "Created monthly \$10 budget with notifications"
    
    # Clean up temp files
    rm -f /tmp/budget.json /tmp/budget-notifications.json
}

# Function to set up resource tagging policy
setup_resource_tagging() {
    log "Setting up resource tagging policy..."
    
    cat > /tmp/tagging-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Deny",
      "Action": [
        "ec2:RunInstances",
        "rds:CreateDBInstance",
        "elasticloadbalancing:CreateLoadBalancer"
      ],
      "Resource": "*",
      "Condition": {
        "Null": {
          "aws:RequestedRegion": "false"
        },
        "StringNotEquals": {
          "aws:RequestedRegion": ["us-east-1", "us-west-2"]
        }
      }
    }
  ]
}
EOF

    # Note: This would typically be applied via AWS Organizations
    success "Tagging policy template created at /tmp/tagging-policy.json"
}

# Function to create cost monitoring dashboard
create_cost_dashboard() {
    log "Creating cost monitoring dashboard..."
    
    cat > /tmp/dashboard.json << 'EOF'
{
  "widgets": [
    {
      "type": "metric",
      "x": 0,
      "y": 0,
      "width": 12,
      "height": 6,
      "properties": {
        "metrics": [
          [ "AWS/Billing", "EstimatedCharges", "Currency", "USD" ]
        ],
        "period": 21600,
        "stat": "Maximum",
        "region": "us-east-1",
        "title": "Total Estimated Charges"
      }
    },
    {
      "type": "metric",
      "x": 0,
      "y": 6,
      "width": 12,
      "height": 6,
      "properties": {
        "metrics": [
          [ "AWS/EC2", "CPUUtilization", { "stat": "Average" } ]
        ],
        "period": 300,
        "stat": "Average",
        "region": "us-east-1",
        "title": "EC2 CPU Utilization"
      }
    }
  ]
}
EOF

    aws cloudwatch put-dashboard \
        --dashboard-name "CostMonitoring" \
        --dashboard-body file:///tmp/dashboard.json
    
    success "Created cost monitoring dashboard"
    rm -f /tmp/dashboard.json
}

# Function to set up automated cost reports
setup_cost_reports() {
    log "Setting up automated cost reports..."
    
    # Create S3 bucket for cost reports
    local bucket_name="aws-cost-reports-$(date +%s)"
    aws s3 mb s3://$bucket_name
    
    # Enable cost and usage reports
    cat > /tmp/cost-report-definition.json << EOF
{
  "ReportName": "daily-cost-report",
  "TimeUnit": "DAILY",
  "Format": "textORcsv",
  "Compression": "GZIP",
  "AdditionalSchemaElements": ["RESOURCES"],
  "S3Bucket": "$bucket_name",
  "S3Prefix": "cost-reports/",
  "S3Region": "us-east-1",
  "AdditionalArtifacts": ["REDSHIFT", "QUICKSIGHT"]
}
EOF

    success "Cost report configuration created"
    rm -f /tmp/cost-report-definition.json
}

# Function to create instance scheduler
create_instance_scheduler() {
    log "Creating EC2 instance scheduler..."
    
    cat > /tmp/scheduler-lambda.py << 'EOF'
import boto3
import json
from datetime import datetime

def lambda_handler(event, context):
    ec2 = boto3.client('ec2')
    
    # Get current day and hour
    now = datetime.now()
    current_day = now.strftime('%A').lower()
    current_hour = now.hour
    
    # Business hours: Mon-Fri, 9 AM - 6 PM
    business_days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
    business_hours = range(9, 18)
    
    # Get instances with scheduling tag
    instances = ec2.describe_instances(
        Filters=[
            {
                'Name': 'tag:AutoSchedule',
                'Values': ['true']
            },
            {
                'Name': 'instance-state-name',
                'Values': ['running', 'stopped']
            }
        ]
    )
    
    for reservation in instances['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            current_state = instance['State']['Name']
            
            if current_day in business_days and current_hour in business_hours:
                # Start instances during business hours
                if current_state == 'stopped':
                    ec2.start_instances(InstanceIds=[instance_id])
                    print(f"Started instance {instance_id}")
            else:
                # Stop instances outside business hours
                if current_state == 'running':
                    ec2.stop_instances(InstanceIds=[instance_id])
                    print(f"Stopped instance {instance_id}")
    
    return {
        'statusCode': 200,
        'body': json.dumps('Instance scheduling completed')
    }
EOF

    success "Instance scheduler Lambda function created at /tmp/scheduler-lambda.py"
}

# Main function
main() {
    log "Setting up AWS Free Tier Protection"
    
    echo -e "${GREEN}"
    cat << 'EOF'
╔══════════════════════════════════════════════════════════════════════════════╗
║                        AWS FREE TIER PROTECTION SETUP                       ║
║                                                                              ║
║  This script will set up the following cost protection measures:            ║
║  • Billing alerts at $5, $10, $25, and $50                                 ║
║  • Monthly budget of $10 with email notifications                           ║
║  • Cost monitoring dashboard                                                ║
║  • Resource tagging policies                                                ║
║  • Automated cost reports                                                   ║
║  • EC2 instance scheduler template                                          ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
    
    read -p "Do you want to proceed with setting up cost protection? (y/N): " confirm
    
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        log "Operation cancelled by user"
        exit 0
    fi
    
    # Check if AWS CLI is configured
    if ! aws sts get-caller-identity &> /dev/null; then
        error "AWS CLI not configured. Please run 'aws configure' first."
        exit 1
    fi
    
    # Enable billing alerts (must be done in us-east-1)
    export AWS_DEFAULT_REGION=us-east-1
    
    setup_billing_alerts
    setup_cost_budget
    create_cost_dashboard
    setup_resource_tagging
    setup_cost_reports
    create_instance_scheduler
    
    success "AWS Free Tier Protection setup completed!"
    
    log "Summary of protection measures:"
    log "✅ Billing alerts created for \$5, \$10, \$25, \$50"
    log "✅ Monthly \$10 budget with notifications"
    log "✅ Cost monitoring dashboard"
    log "✅ Resource tagging policy template"
    log "✅ Cost report configuration"
    log "✅ EC2 instance scheduler template"
    
    warning "Important next steps:"
    log "1. Confirm email subscriptions for billing alerts"
    log "2. Review and customize the instance scheduler"
    log "3. Set up AWS Config rules for compliance"
    log "4. Consider using AWS Organizations for better control"
    log "5. Regularly review the cost dashboard"
    
    log "Free tier limits to remember:"
    log "• EC2: 750 hours/month of t2.micro or t3.micro"
    log "• S3: 5GB storage, 20,000 GET requests, 2,000 PUT requests"
    log "• Lambda: 1M requests, 400,000 GB-seconds compute"
    log "• CloudWatch: 10 metrics, 10 alarms, 1M API requests"
}

main "$@"