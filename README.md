# SS Crypto Data Mining (HFT Data)
Easily set up and deploy your crypto data mining application to use with Strategy Studio for your next high-frequency trading (HFT) project.

## 🚀 Getting Started

### 🔧 Prerequisites

1. **Docker and Docker Compose**  
   Allows you to containerize and manage the application services.  
   🌐 [Download Docker](www.docker.com)

2. **Python 3.9+**  
   Ensure you have the latest Python version for the best experience.  
   🌐 [Download Python](https://www.python.org/downloads/)

## Author

### **Saranpat Prasertthum (sp73@illinois.edu)**

* My name is **Saranpat Prasertthum**, and I am currently pursuing my **Master's in Financial Engineering** at the University of Illinois at Urbana-Champaign, with an expected graduation in December 2023. My academic journey has equipped me with knowledge in High Frequency Trading, Stochastic Calculus, and Algorithmic Trading. Professionally, I spent **two years as a Software Engineer** at Blockfint, a startup company. I am proficient in languages such as **Python, C++, Go, Java, and JavaScript, and have a strong background in SQL**. Additionally, I have hands-on experience as a **backend developer** and am well-versed in cloud platforms. My areas of interest encompass **high-performance computing, finance, and trading**. My Linkedin is located at: **https://www.linkedin.com/in/saranpatp**

## 📦 Deployment

### Using Docker:
1. Build and start the containers:
    ```
    docker-compose build
    docker-compose up -d
    ```

### Running Locally:
1. Install necessary Python packages:
    ```
    pip install -r requirements.txt
    ```

2. Start the application:
    ```
    python multi_exchange_socket_orderbook.py
    ```