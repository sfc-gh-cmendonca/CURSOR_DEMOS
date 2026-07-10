#!/bin/bash
set -e

REGION="eu-central-1"
INSTANCE_TYPE="m5.xlarge"
AMI_ID="ami-0a628e1e89aaedf80"  # Amazon Linux 2023 in eu-central-1
KEY_NAME="rdp-harness-key"
SG_NAME="rdp-harness-sg"
INSTANCE_NAME="rdp-test-harness"

echo "=== RDP Test Harness - EC2 Deployment ==="
echo "Region: $REGION"
echo ""

# Step 1: Create key pair
echo "[1/5] Creating key pair..."
aws ec2 create-key-pair \
    --region "$REGION" \
    --key-name "$KEY_NAME" \
    --query 'KeyMaterial' \
    --output text > "${KEY_NAME}.pem"
chmod 400 "${KEY_NAME}.pem"
echo "  Key saved to ${KEY_NAME}.pem"

# Step 2: Create security group
echo "[2/5] Creating security group..."
VPC_ID=$(aws ec2 describe-vpcs --region "$REGION" --filters "Name=isDefault,Values=true" --query 'Vpcs[0].VpcId' --output text)
SG_ID=$(aws ec2 create-security-group \
    --region "$REGION" \
    --group-name "$SG_NAME" \
    --description "RDP Test Harness - SSH and Streamlit" \
    --vpc-id "$VPC_ID" \
    --query 'GroupId' \
    --output text)

# Allow SSH and Streamlit port
MY_IP=$(curl -s https://checkip.amazonaws.com)
aws ec2 authorize-security-group-ingress --region "$REGION" --group-id "$SG_ID" \
    --protocol tcp --port 22 --cidr "${MY_IP}/32"
aws ec2 authorize-security-group-ingress --region "$REGION" --group-id "$SG_ID" \
    --protocol tcp --port 8501 --cidr "${MY_IP}/32"
echo "  Security group $SG_ID created (SSH + 8501 from $MY_IP)"

# Step 3: Launch instance
echo "[3/5] Launching EC2 instance ($INSTANCE_TYPE)..."
INSTANCE_ID=$(aws ec2 run-instances \
    --region "$REGION" \
    --image-id "$AMI_ID" \
    --instance-type "$INSTANCE_TYPE" \
    --key-name "$KEY_NAME" \
    --security-group-ids "$SG_ID" \
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=$INSTANCE_NAME}]" \
    --block-device-mappings '[{"DeviceName":"/dev/xvda","Ebs":{"VolumeSize":30,"VolumeType":"gp3"}}]' \
    --query 'Instances[0].InstanceId' \
    --output text)
echo "  Instance: $INSTANCE_ID"

echo "  Waiting for instance to be running..."
aws ec2 wait instance-running --region "$REGION" --instance-ids "$INSTANCE_ID"

PUBLIC_IP=$(aws ec2 describe-instances \
    --region "$REGION" \
    --instance-ids "$INSTANCE_ID" \
    --query 'Reservations[0].Instances[0].PublicIpAddress' \
    --output text)
echo "  Public IP: $PUBLIC_IP"

# Step 4: Wait for SSH to be ready
echo "[4/5] Waiting for SSH..."
sleep 30
until ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 -i "${KEY_NAME}.pem" ec2-user@"$PUBLIC_IP" "echo ready" 2>/dev/null; do
    sleep 5
done

# Step 5: Setup the instance
echo "[5/5] Installing dependencies and deploying harness..."

ssh -i "${KEY_NAME}.pem" ec2-user@"$PUBLIC_IP" << 'REMOTE_SETUP'
set -e

# Install Java and Python
sudo dnf install -y java-17-amazon-corretto python3.11 python3.11-pip git
sudo alternatives --set java /usr/lib/jvm/java-17-amazon-corretto.aarch64/bin/java 2>/dev/null || true

# Install Python packages
pip3.11 install --user streamlit jaydebeapi jpype1 pandas

# Create app directory
mkdir -p ~/rdp_harness/lib ~/rdp_harness/keys ~/rdp_harness/.streamlit

echo "Dependencies installed."
REMOTE_SETUP

# Copy the harness files
echo "  Copying harness files..."
scp -i "${KEY_NAME}.pem" app.py ec2-user@"$PUBLIC_IP":~/rdp_harness/
scp -i "${KEY_NAME}.pem" lib/snowflake-jdbc.jar ec2-user@"$PUBLIC_IP":~/rdp_harness/lib/
scp -i "${KEY_NAME}.pem" keys/rsa_key.p8 ec2-user@"$PUBLIC_IP":~/rdp_harness/keys/

# Update JAVA_HOME for Amazon Corretto
ssh -i "${KEY_NAME}.pem" ec2-user@"$PUBLIC_IP" << 'PATCH'
sed -i 's|/opt/homebrew/opt/openjdk/libexec/openjdk.jdk/Contents/Home|/usr/lib/jvm/java-17-amazon-corretto.aarch64|g' ~/rdp_harness/app.py
PATCH

# Create a start script
ssh -i "${KEY_NAME}.pem" ec2-user@"$PUBLIC_IP" << 'START_SCRIPT'
cat > ~/rdp_harness/start.sh << 'EOF'
#!/bin/bash
export JAVA_HOME=/usr/lib/jvm/java-17-amazon-corretto.aarch64
cd ~/rdp_harness
nohup python3.11 -m streamlit run app.py --server.port 8501 --server.headless true --server.address 0.0.0.0 > streamlit.log 2>&1 &
echo "Streamlit started on port 8501"
echo "Access at: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):8501"
EOF
chmod +x ~/rdp_harness/start.sh
~/rdp_harness/start.sh
START_SCRIPT

echo ""
echo "=== DEPLOYMENT COMPLETE ==="
echo ""
echo "  Instance ID:  $INSTANCE_ID"
echo "  Public IP:    $PUBLIC_IP"
echo "  Harness URL:  http://${PUBLIC_IP}:8501"
echo "  SSH:          ssh -i ${KEY_NAME}.pem ec2-user@${PUBLIC_IP}"
echo ""
echo "  To stop:      aws ec2 stop-instances --region $REGION --instance-ids $INSTANCE_ID"
echo "  To terminate: aws ec2 terminate-instances --region $REGION --instance-ids $INSTANCE_ID"
echo ""
