# LifeLine AWS Cloud Infrastructure & DevOps Blueprint

> **Architecture Tier**: High-Availability Cloud Deployment without Docker  
> **AWS Free Tier / Cost-Optimized**: EC2 (`t2/t3.micro`), RDS PostgreSQL (`db.t3.micro`), S3 (SSE-S3), SNS/SES, CloudWatch  
> **Scalability Strategy**: Application Load Balancer (ALB) + Auto Scaling Group (ASG) for Sudden Disaster & Regional Emergency Surges  

---

## 1. High-Availability Crisis Architecture

During major catastrophes, multi-casualty incidents, or sudden rare blood shortages (e.g., pediatric trauma needing ultra-rare **Bombay $O_h$** or **Rh-null**), web traffic spikes 100x. LifeLine scales elastically without container orchestration overhead:

```
                           ┌────────────────────────────┐
                           │   Internet Client Traffic  │
                           └─────────────┬──────────────┘
                                         │ HTTPS:443 / HTTP:80
                                         ▼
                     ┌───────────────────────────────────────┐
                     │    AWS Application Load Balancer      │
                     │  - SSL/TLS Termination (ACM Cert)     │
                     │  - Health Check: GET /healthz         │
                     └───────────────────┬───────────────────┘
                                         │
                    ┌────────────────────┴────────────────────┐
                    ▼                                         ▼
   ┌─────────────────────────────────┐       ┌─────────────────────────────────┐
   │    EC2 Instance 1 (Primary)     │       │    EC2 Instance 2 (Scale-out)   │
   │  ┌───────────────────────────┐  │       │  ┌───────────────────────────┐  │
   │  │ Nginx (Port 80)           │  │       │  │ Nginx (Port 80)           │  │
   │  │ - React SPA Static Build  │  │       │  │ - React SPA Static Build  │  │
   │  └─────────────┬─────────────┘  │       │  └─────────────┬─────────────┘  │
   │                │ Proxy /api     │       │                │ Proxy /api     │
   │                ▼                │       │                ▼                │
   │  ┌───────────────────────────┐  │       │  ┌───────────────────────────┐  │
   │  │ FastAPI / Systemd (8000)  │  │       │  │ FastAPI / Systemd (8000)  │  │
   │  │ - 2 Uvicorn Workers       │  │       │  │ - 2 Uvicorn Workers       │  │
   │  └─────────────┬─────────────┘  │       │  └─────────────┬─────────────┘  │
   └────────────────┼────────────────┘       └────────────────┼────────────────┘
                    │                                         │
                    └────────────────────┬────────────────────┘
                                         │
         ┌───────────────────────────────┼───────────────────────────────┐
         ▼                               ▼                               ▼
┌──────────────────┐           ┌──────────────────┐           ┌──────────────────┐
│ AWS RDS Postgres │           │ AWS S3 Vault     │           │ AWS SNS & SES    │
│ - db.t3.micro    │           │ - SSE-S3 AES-256 │           │ - Priority SMS   │
│ - 5 Pool Conns   │           │ - Private Bucket │           │ - Regional SES   │
└──────────────────┘           └──────────────────┘           └──────────────────┘
```

---

## 2. EC2 Launch Template & Auto Scaling Group (ASG)

### A. Launch Template Configuration
- **Template Name**: `lifeline-web-node-v1`
- **AMI**: Ubuntu Server 22.04 LTS (HVM), SSD Volume Type (`ami-0c7217cdde317cfec` in `us-east-1` or latest)
- **Instance Type**: `t3.micro` (or `t2.micro` for AWS Free Tier)
- **IAM Instance Profile**: `LifeLine-EC2-AppRole` (No hardcoded credentials on instances)
- **Security Group (`lifeline-ec2-sg`)**:
  - Inbound: Port 80 from `lifeline-alb-sg`
  - Inbound: Port 22 from Administrator Bastion / VPN IP
  - Outbound: All traffic (`0.0.0.0/0`)
- **Block Device Mapping**: 25 GB gp3 root volume

#### User Data Script (Automates Bootstrapping on Scale-out):
```bash
#!/bin/bash
set -euo pipefail

# Update and install system packages
export DEBIAN_FRONTEND=noninteractive
apt-get update -y
apt-get install -y git python3 python3-pip python3-venv nginx curl

# Clone LifeLine repository
cd /home/ubuntu
if [ ! -d "/home/ubuntu/lifeline" ]; then
    sudo -u ubuntu git clone https://github.com/your-org/lifeline.git /home/ubuntu/lifeline
fi

cd /home/ubuntu/lifeline
# Run automated EC2 provisioning
bash scripts/setup_ec2.sh

# Configure environment variables from AWS Systems Manager Parameter Store or S3
# aws ssm get-parameter --name "/lifeline/production/env" --with-decryption --query "Parameter.Value" --output text > /home/ubuntu/lifeline/backend/.env

systemctl restart lifeline.service
systemctl restart nginx
```

---

### B. Application Load Balancer (ALB) Setup
1. **Target Group (`lifeline-tg-80`)**:
   - **Target Type**: Instances
   - **Protocol**: HTTP | **Port**: 80
   - **Health Check Path**: `/healthz`
   - **Health Check Port**: `traffic-port`
   - **Healthy Threshold**: 2 | **Unhealthy Threshold**: 3
   - **Timeout**: 5 seconds | **Interval**: 15 seconds
2. **ALB Listener**:
   - `HTTP (Port 80)` -> Redirect to `HTTPS (Port 443)` with HTTP 301
   - `HTTPS (Port 443)` -> Forward to `lifeline-tg-80` with ACM SSL certificate

---

### C. Auto Scaling Group (ASG) Scaling Policies
- **Name**: `lifeline-asg-production`
- **Minimum Capacity**: 1 instance (Free Tier default)
- **Desired Capacity**: 1 instance
- **Maximum Capacity**: 4 instances (Expands rapidly during mass casualties or crisis campaigns)
- **VPC Subnets**: Across at least 2 Availability Zones (`us-east-1a`, `us-east-1b`)
- **Target Tracking Policy 1 (CPU Spike Protection)**:
  - Metric: `ASGAverageCPUUtilization`
  - Target Value: `70%`
  - Warmup period: `180 seconds`
- **Target Tracking Policy 2 (Emergency Request Surge Protection)**:
  - Metric: `ALBRequestCountPerTarget`
  - Target Value: `1200` requests per instance

---

## 3. AWS S3 Medical Document Vault Policy

Stores donor medical fitness records and official hospital requisitions.

### A. S3 Bucket Policy (Enforce SSE-S3 AES-256 & HTTPS-Only)
Replace `lifeline-medical-documents` with your unique bucket name:

```json
{
  "Version": "2012-10-17",
  "Id": "LifeLineS3SecurityPolicy",
  "Statement": [
    {
      "Sid": "DenyNonSecureTransportHTTPS",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:*",
      "Resource": [
        "arn:aws:s3:::lifeline-medical-documents",
        "arn:aws:s3:::lifeline-medical-documents/*"
      ],
      "Condition": {
        "Bool": {
          "aws:SecureTransport": "false"
        }
      }
    },
    {
      "Sid": "EnforceServerSideEncryptionAES256",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::lifeline-medical-documents/*",
      "Condition": {
        "StringNotEquals": {
          "s3:x-amz-server-side-encryption": "AES256"
        }
      }
    },
    {
      "Sid": "DenyUnencryptedObjectUploads",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::lifeline-medical-documents/*",
      "Condition": {
        "Null": {
          "s3:x-amz-server-side-encryption": "true"
        }
      }
    }
  ]
}
```

### B. S3 Block Public Access (All 4 Enabled)
- `BlockPublicAcls`: **TRUE**
- `IgnorePublicAcls`: **TRUE**
- `BlockPublicPolicy`: **TRUE**
- `RestrictPublicBuckets`: **TRUE**
*(Direct public access is completely blocked. Authorized users view documents exclusively via pre-signed URLs with a 3600-second expiration time)*

### C. S3 CORS Configuration (Permits Browser PUT Uploads via Presigned URLs)
```json
[
  {
    "AllowedHeaders": [
      "Content-Type",
      "x-amz-server-side-encryption"
    ],
    "AllowedMethods": [
      "PUT",
      "GET"
    ],
    "AllowedOrigins": [
      "https://lifeline-emergency.org",
      "http://localhost:3000"
    ],
    "ExposeHeaders": [
      "ETag"
    ],
    "MaxAgeSeconds": 3600
  }
]
```

---

## 4. IAM Least-Privilege Policies

Attach to the EC2 Instance Profile Role (`LifeLine-EC2-AppRole`).

### Policy 1: `LifeLine-S3-Vault-Policy`
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "S3BucketAccess",
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket",
        "s3:GetBucketLocation"
      ],
      "Resource": "arn:aws:s3:::lifeline-medical-documents"
    },
    {
      "Sid": "S3ObjectOperationsWithSSE",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject"
      ],
      "Resource": [
        "arn:aws:s3:::lifeline-medical-documents/health-clearances/*",
        "arn:aws:s3:::lifeline-medical-documents/hospital-verifications/*"
      ]
    }
  ]
}
```

### Policy 2: `LifeLine-SNS-SES-Alert-Policy`
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "SNSTransactionalSMSPublish",
      "Effect": "Allow",
      "Action": [
        "sns:Publish",
        "sns:SetSMSAttributes",
        "sns:GetSMSAttributes"
      ],
      "Resource": "*"
    },
    {
      "Sid": "SESEmailBroadcast",
      "Effect": "Allow",
      "Action": [
        "ses:SendEmail",
        "ses:SendRawEmail"
      ],
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "ses:FromAddress": "alerts@lifeline-emergency.org"
        }
      }
    }
  ]
}
```

---

## 5. AWS CloudWatch Metrics & Crisis Alarm Setup

Configure CloudWatch Alarms to automatically monitor and alert engineers via SNS when infrastructure is under strain.

### Alarm 1: High CPU Utilization (> 80%)
- **Metric Name**: `CPUUtilization`
- **Namespace**: `AWS/EC2`
- **Statistic**: `Average`
- **Period**: `60 seconds`
- **Evaluation Periods**: 2 (2 consecutive minutes above 80%)
- **Threshold**: `>= 80%`
- **Action**: Publish notification to `arn:aws:sns:us-east-1:123456789012:lifeline-devops-alerts`

#### AWS CLI Setup Command:
```bash
aws cloudwatch put-metric-alarm \
    --alarm-name "LifeLine-HighCPU-Alarm" \
    --alarm-description "Triggers when LifeLine EC2 CPU exceeds 80% for 2 minutes" \
    --metric-name CPUUtilization \
    --namespace AWS/EC2 \
    --statistic Average \
    --period 60 \
    --threshold 80 \
    --comparison-operator GreaterThanOrEqualToThreshold \
    --evaluation-periods 2 \
    --alarm-actions "arn:aws:sns:us-east-1:123456789012:lifeline-devops-alerts" \
    --dimensions Name=AutoScalingGroupName,Value=lifeline-asg-production
```

---

### Alarm 2: API 5xx Server Error Rate
- **Metric Name**: `HTTPCode_Target_5XX_Count`
- **Namespace**: `AWS/ApplicationELB`
- **Statistic**: `Sum`
- **Period**: `60 seconds`
- **Evaluation Periods**: 1
- **Threshold**: `>= 5` errors per minute
- **Action**: High-priority alert to on-call engineers

#### AWS CLI Setup Command:
```bash
aws cloudwatch put-metric-alarm \
    --alarm-name "LifeLine-API-5xx-Alert" \
    --alarm-description "Triggers when ALB encounters 5 or more 5xx backend responses in 1 minute" \
    --metric-name HTTPCode_Target_5XX_Count \
    --namespace AWS/ApplicationELB \
    --statistic Sum \
    --period 60 \
    --threshold 5 \
    --comparison-operator GreaterThanOrEqualToThreshold \
    --evaluation-periods 1 \
    --alarm-actions "arn:aws:sns:us-east-1:123456789012:lifeline-devops-alerts" \
    --dimensions Name=TargetGroup,Value=targetgroup/lifeline-tg-80/a1b2c3d4e5
```
