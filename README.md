# Frameshift Sonification Tool

A bioinformatics tool that converts DNA sequences into audible MIDI music to visualize and study frameshift mutations and genetic alignment data. This MSc Research Project transforms BLAST protein alignment data into a musical representation, making frameshift mutations sonically perceptible.

## Overview

This tool processes BLAST (Basic Local Alignment Search Tool) XML output files and converts the aligned DNA sequences into MIDI audio files. Each nucleotide and codon is mapped to a musical note, allowing researchers to:

- **Audibly identify frameshifts** - gaps and shifts in sequences create distinctive sonic markers
- **Compare sequence alignments** - query and subject sequences play as separate MIDI tracks simultaneously
- **Analyze at multiple levels** - view alignments both at the nucleotide and codon level
- **Explore reading frames** - examine different reading frames of the sequence

### Key Scientific Mappings

- **Nucleotides**: A, C, G, T mapped to specific MIDI notes (based on Plaisier et al. 2021)
- **Codons**: Amino acids mapped to MIDI notes (based on Edwards et al. 2021, PMID: 34556048)
- **Stop Codons**: Distinctive percussion sound to mark translation termination
- **Gaps**: Cymbal clash sound to highlight sequence misalignments

---

## Architecture

### Core Components

```
frameshift_sonification/
├── app/                          # Flask web application
│   ├── flask_app.py             # Main Flask application & routing
│   ├── sonification_functions.py # Core sonification logic
│   ├── sound_mappings.py        # Nucleotide & codon-to-MIDI mappings
│   ├── settings.py              # App configuration
│   ├── templates/               # HTML templates (UI)
│   └── static/                  # CSS, images, client-side assets
├── terraform/                    # AWS infrastructure as code
│   ├── main.tf                  # Main provider & module definitions
│   ├── variables.tf             # Configuration variables
│   ├── outputs.tf               # Terraform outputs
│   ├── modules/
│   │   ├── vpc/                 # VPC, subnets, networking
│   │   └── ecs/                 # ECS Fargate cluster & service
│   └── terraform.tf             # Terraform backend config
├── Dockerfile                    # Docker container definition
├── requirements.txt             # Python dependencies
└── test_files/                  # Example BLAST XML files
```

### Component Descriptions

#### 1. Flask Web Application (`app/`)

The core web interface and API for the sonification tool.

**Main Routes:**
- `GET/POST /` - Upload BLAST XML file or load example dataset
- `GET /alignments` - Display list of alignments from uploaded file
- `GET /alignments/<index>` - View detailed alignment and sonification controls
- `POST /alignments/sonify` - Generate MIDI file from selected alignment
- `GET /temp/<filename>` - Serve generated MIDI files for playback

**Key Features:**
- Session-based state management for handling multiple users
- XML parsing of BLAST output using BioPython
- Real-time MIDI file generation with configurable parameters
- Temporary file management for generated audio

**Configuration** (`settings.py`):
```python
out_file_path = "/flask_app/temp"  # MIDI output directory
secret_key = "put_your_super_secret_key_here"
example_file = "test_files/example_data_set.xml"
```

#### 2. Sonification Engine (`app/sonification_functions.py`)

The heart of the project - converts sequences to MIDI.

**Main Functions:**

- `build_track()` - Master function that orchestrates multi-channel MIDI generation
  - Supports nucleotide and codon sonification simultaneously
  - Implements reading frame offsets
  - Handles stop codon detection
  - Uses multiple MIDI channels for different sequence elements

- `build_track_nuc()` - Generates nucleotide track (For reference - not used in the flask app)
  - Maps individual bases to MIDI pitches
  - Uses channel 0 for regular notes, channel 9 (percussion) for gaps

- `build_track_codon()` - Generates codon track (For reference - not used in the flask app)
  - Groups bases into codons and maps to amino acid notes
  - Maintains reading frame continuity
  - Uses dedicated channel for stop codons

**Parameters:**
- `reading_frame` - Which reading frame to use (1, 2, or 3)
- `stop` - Stop sonification at stop codon if True
- `codons` - Include codon-level sonification
- `nucs` - Include nucleotide-level sonification

#### 3. Sound Mappings (`sound_mappings.py`)

Scientific mappings of biological sequences to musical notes.

**Base Mapping** (Nucleotides):
```python
base_map = {
    "A": 69,  # A5
    "T": 63,  # D#5
    "G": 67,  # G5
    "C": 60   # C5
}
```

**Codon Mapping** (Amino Acids):
- Maps all 64 codons to their corresponding amino acids
- Each amino acid has a unique MIDI note (50-77)
- Stop codons (TAA, TAG, TGA) trigger percussion (note 39)

#### 4. Docker Containerization

**Dockerfile** builds a self-contained application environment:

- **Base Image**: Ubuntu  (latest stable)
- **Python Version**: 3.12
- **Setup**:
  - Creates Python virtual environment
  - Installs all dependencies
  - Creates required temp directories for MIDI output
  - Exposes port 5001 (configurable)
  - Runs Flask app with `python app/flask_app.py`

**Key Points:**
- Uses multi-stage builds for efficiency
- Virtual environment isolates dependencies
- Temp directory mounted as volume for file persistence

#### 5. Terraform AWS Infrastructure

Complete Infrastructure-as-Code for deployment on AWS.

**Architecture Overview:**

```
┌─────────────────────────────────────┐
│        Internet / Users             │
└──────────────┬──────────────────────┘
               │
      ┌────────▼────────┐
      │   Load Balancer │
      │    (ALB)        │
      └────────┬────────┘
               │
      ┌────────▼────────────────┐
      │  VPC: 10.0.0.0/16       │
      │  ┌──────────────────┐   │
      │  │ Public Subnets   │   │
      │  │ 10.0.2-3.0/24    │   │
      │  └──────────────────┘   │
      │  ┌──────────────────┐   │
      │  │ Private Subnet   │   │
      │  │ 10.0.1.0/24      │   │
      │  │ ┌──────────────┐ │   │
      │  │ │ ECS Fargate  │ │   │
      │  │ │ Tasks        │ │   │
      │  │ └──────────────┘ │   │
      │  └──────────────────┘   │
      └─────────────────────────┘
```

**VPC Module** (`terraform/modules/vpc/main.tf`):
- Virtual Private Cloud (10.0.0.0/16 CIDR)
- Two public subnets for load balancer
- One private subnet for ECS tasks
- Internet Gateway for public access
- NAT Gateway for private subnet outbound traffic

**ECS Module** (`terraform/modules/ecs/main.tf`):
- **Cluster**: ECS cluster for container orchestration
- **Task Definition**: Fargate-compatible task with:
  - CPU: 256 units
  - Memory: 2048 MB
  - Container port: 5001
  - CloudWatch logging
- **Service**: Manages 1 task by default
- **Load Balancer**: Application Load Balancer (ALB)
  - HTTP listener on port 80
  - Routes to ECS tasks
  - Health checks configured
- **Security Groups**: Control traffic between components
- **IAM Roles**: Permissions for ECS task execution

**Variables** (`terraform/variables.tf`):
- `app_name`: Application identifier (default: "frameshift")
- `container_image`: ECR image URI
- `container_port`: Container port (default: 5001)
- `vpc_cidr`, subnet CIDRs: Network configuration

**Deployment Flow:**
1. Docker image pushed to AWS ECR
2. Terraform creates VPC and networking
3. ECS task definition references ECR image
4. ECS service launches container in private subnet
5. ALB routes external traffic to containers

---

## Getting Started

### Local Development

#### Prerequisites
- Python 3.12+
- pip or pip3
- Virtual environment tool (venv)

#### Setup

1. **Clone and navigate to project**:
```bash
cd /path/to/frameshift_sonification
```

2. **Create and activate virtual environment**:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Configure settings** (optional):
Edit `app/settings.py` to customize:
- MIDI output directory
- Flask secret key (for production)
- Example data file path

5. **Run the Flask app**:
```bash
python app/flask_app.py
```

6. **Access in browser**:
```
http://localhost:5001
```

### Docker Deployment (Local)

1. **Build Docker image**:
```bash
docker build -t sonification-app:latest .
```

2. **Run container**:
```bash
docker run -p 5001:5001 sonification-app:latest
```

3. **Access the app**:
```
http://localhost:5001
```

### AWS Deployment with Terraform

#### Prerequisites
- AWS Account with credentials configured
- Terraform 1.0+
- AWS CLI configured
- Docker image pushed to ECR at: `<account>.dkr.ecr.eu-west-2.amazonaws.com/sonification/sonification_app:latest`

#### Deployment Steps

1. **Navigate to terraform directory**:
```bash
cd terraform
```

2. **Initialize Terraform**:
```bash
terraform init
```

3. **Review planned changes**:
```bash
terraform plan
```

4. **Apply infrastructure**:
```bash
terraform apply
```

5. **Get load balancer URL**:
```bash
terraform output alb_dns_name
```

6. **Access the application**:
```
http://<alb_dns_name>
```

#### Destroying Infrastructure
```bash
terraform destroy
```

---

## Usage Guide

### Uploading and Processing BLAST Files

1. **Start the application** (local or AWS)
2. **Upload a BLAST XML file**:
   - Click "Choose File" and select your BLAST XML output
   - Or click "Load Example" to test with sample data
3. **View alignments**:
   - Browse through detected alignments in the result set
4. **Select an alignment**:
   - Click on any alignment to view details
   - See query and subject sequences
5. **Configure sonification**:
   - Select **Reading Frame** (1, 2, or 3)
   - Choose **Codon/Nucleotide** mode:
     - Nucleotides only (detailed single-base view)
     - Codons only (protein-level view)
     - Both (multi-channel MIDI)
   - Check "Stop at stop codon" to end sonification at TAA/TAG/TGA
6. **Generate MIDI**:
   - Click "Generate MIDI" to create audio file
   - Browser plays audio directly via Web Audio API
7. **Download or replay**:
   - Generated MIDI files can be downloaded
   - Playback quality depends on your device's MIDI synthesizer

### Interpreting the Audio

**Sonic Elements:**
- **Rising/Falling Pitches**: Different nucleotides or codons
- **Gaps (Cymbal Clash)**: Alignment mismatches
- **Percussion Sound**: Stop codons (translation termination)
- **Two Simultaneous Melodies**: Query vs. subject sequences
- **Tempo**: Fixed at 140 BPM

**Detecting Frameshifts:**
Frameshifts create discontinuities in the codon melody - the pitch sequence becomes unexpected after the shift point, making frameshifts immediately apparent sonically.

---

## Project Dependencies

### Python Packages
- **flask** (3.1.3+) - Web framework
- **flask-session** (0.8.0+) - Session management
- **bio** (1.8.3+) - BioPython for sequence handling
- **midiutil** (1.2.1+) - MIDI file generation
- **pygame** (2.6.1+) - Audio playback support
- **datetime** (6.0+) - Timestamp utilities

### System Dependencies
- Python 3.12
- MIDI synthesizer (system audio)

---

## File Structure Reference

| File | Purpose |
|------|---------|
| `app/flask_app.py` | Main Flask application & routes |
| `app/sonification_functions.py` | Sequence-to-MIDI conversion logic |
| `app/sound_mappings.py` | Nucleotide & codon mappings |
| `app/settings.py` | Configuration settings |
| `terraform/main.tf` | AWS resources & module composition |
| `terraform/modules/vpc/main.tf` | VPC and networking resources |
| `terraform/modules/ecs/main.tf` | Container orchestration setup |
| `Dockerfile` | Container image definition |
| `requirements.txt` | Python dependencies |

---

## Key Concepts

### Reading Frames
DNA can be read in three different frames (starting at position 0, 1, or 2). Each frame produces a different amino acid sequence. Frameshifts shift which frame is being read, creating different proteins.

### BLAST XML Format
The application expects XML output from BLAST, which contains:
- Query sequences
- Subject/hit sequences
- Alignment information (e-value, bit score, matching regions)
- Frame information (reading frame offset)

### MIDI Channels
The application uses multiple MIDI channels for rich sonification:
- **Channel 0**: Nucleotide notes
- **Channel 1**: Codon/amino acid notes
- **Channel 2**: Stop codon percussion
- **Channel 9**: Gap markers (percussion channel)

### Sonification vs. Visualization
Traditional bioinformatics tools visualize sequences. This tool **sonifies** them - converting data to sound. This auditory approach reveals patterns that might be missed in visual inspection.

---

## Development & Research

This project is an MSc Research Project investigating whether auditory sonification can improve the understanding and detection of frameshift mutations in genetic sequences.

### Relevant Papers
- Plaisier et al. 2021 - Nucleotide sonification approach
- Edwards et al. 2021 (PMID: 34556048) - Codon-to-amino acid mapping

---

## Troubleshooting

### Flask App Won't Start
- Ensure Python 3.12+ is installed
- Check all dependencies: `pip install -r requirements.txt`
- Verify the secret key in `app/settings.py` is set

### No MIDI Output
- Check that `/flask_app/temp` directory exists and is writable
- Verify the BLAST XML file is properly formatted
- Check Flask logs for parsing errors

### Docker Build Fails
- Ensure Dockerfile is in project root
- Check that all source files are present
- Verify Docker daemon is running

### Terraform Deployment Fails
- Verify AWS credentials are configured
- Check AWS account has ECS, VPC, and ALB permissions
- Ensure ECR image URI is correct
- Review CloudFormation events in AWS console

### MIDI Playback Issues
- Update audio drivers for your OS
- Try a different MIDI synthesizer
- Verify browser supports Web Audio API

---

## License & Attribution

See `app/static/images/attribution.md` for image and asset attributions.

---

## Contact & Support

For questions or issues with this research project, please refer to the project documentation or contact the author through the University of Edinburgh.

---

*Last Updated: 2026-07-22*
