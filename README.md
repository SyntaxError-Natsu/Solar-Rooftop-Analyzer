# Advanced Solar Rooftop Analyzer - India Edition

AI-powered solar assessment tool designed for the Indian market with computer vision analysis and comprehensive financial projections.

## 🚀 Live Demo

**Deployed Application**: [https://huggingface.co/spaces/Natsu-Error/Solar-Rooftop-Analyzer](https://huggingface.co/spaces/Natsu-Error/Solar-Rooftop-Analyzer)

## 🎯 Project Overview

This tool combines computer vision and AI to analyze rooftop images for solar panel installation potential, providing detailed financial analysis optimized for Indian market conditions including government subsidies, local electricity rates, and climate data.

## ⚡ Quick Start

### Prerequisites
- Python 3.8 or higher
- OpenRouter API account (free tier available)

### Installation

1. **Clone the repository**
```
git remote add origin https://github.com/SyntaxError-Natsu/Solar-Rooftop-Analyzer.git
cd solar-rooftop-analyzer
```

2. **Install dependencies**
```
pip install -r requirements.txt
```

3. **Configure environment**
```
cp .env.example .env
```
Edit .env and add your OpenRouter API key

4. **Run the application**
```
streamlit run app.py
```

5. **Access the app**
- Open your browser to `http://localhost:8501`

### Environment Variables
OPENROUTER_API_KEY=your_api_key_here

## 🛠️ Technology Stack

- **Frontend**: Streamlit web application
- **AI/ML**: OpenRouter API (Qwen 2.5 VL models)
- **Computer Vision**: OpenCV for roof detection
- **Deployment**: Hugging Face Spaces
- **Language**: Python 3.8+

## 🇮🇳 Indian Market Optimization

### Financial Parameters
- **Currency**: Indian Rupees (₹) with Lakh notation
- **System Cost**: ₹200 per watt (Indian market pricing)
- **Electricity Rate**: ₹8 per kWh (average Indian rate)
- **Government Subsidy**: 30% (Central Government Solar Subsidy)
- **Climate Data**: 1800 sun hours/year (Indian climate optimized)

### Smart Display Features
- **Lakh Notation**: ₹21L instead of ₹21,00,000
- **Thousand Format**: ₹173k instead of ₹1,73,000
- **Familiar Formats**: Uses Indian numbering conventions

## 🔬 Advanced Analysis Features

### Computer Vision Engine
- **Real Roof Detection**: OpenCV-based area estimation
- **Condition Assessment**: Image quality analysis (sharpness, brightness, contrast)
- **Dynamic Sizing**: System size calculated from actual roof area
- **Confidence Scoring**: Reliability metrics for each analysis

### AI Enhancement Layer
- **Vision Models**: Qwen 2.5 VL series (72B/32B/3B variants)
- **Enhanced Interpretation**: AI analysis of computer vision results
- **Shading Assessment**: Detailed shading condition evaluation
- **Fallback System**: Graceful degradation to CV-only if AI fails

## 📊 Analysis Methods

1. **Computer Vision Only**
   - Fast analysis (1-3 seconds)
   - Works without internet connection
   - Reliable baseline results

2. **CV + AI Enhancement**
   - Comprehensive analysis (5-10 seconds)
   - Enhanced accuracy and insights
   - Detailed shading and orientation assessment

3. **Robust Fallback**
   - Always provides results
   - Handles API failures gracefully
   - Multiple model options

## 🎯 Key Features

- **Dynamic Results**: Each image produces unique analysis
- **Professional Reports**: Downloadable JSON analysis reports
- **Performance Metrics**: Real-time analysis speed and confidence tracking
- **Multiple AI Models**: Choose from 3 free vision models
- **Indian Context**: Localized pricing, subsidies, and climate data

## 📱 Usage Instructions

1. **Upload Image**: Choose clear aerial/satellite rooftop image
2. **Configure Settings**: Select AI model and maximum system size
3. **Choose Method**: CV-only or CV + AI enhancement
4. **Analyze**: Click "Analyze with Computer Vision"
5. **Review Results**: Comprehensive technical and financial analysis
6. **Download Report**: Export detailed JSON report

## 📊 Performance Specifications

- **Analysis Time**: 3-13 seconds total
- **Accuracy**: 75-90% roof area estimation
- **Success Rate**: 95%+ with fallback systems
- **Daily Limit**: 50 free AI requests
- **Supported Formats**: PNG, JPG, JPEG
- **Image Size**: Up to 10MB recommended

## 📁 Project Structure
```
solar-rooftop-analyzer/
├── app.py                  # Main Streamlit application script
├── requirements.txt        # Python dependencies
├── .env.example            # Template for environment variables (e.g., API keys)
├── README.md               # Project documentation (overview, setup, usage)
├── docs/                   # Technical documentation folder
│   ├── implementation.md   # Detailed implementation notes
│   └── examples.md         # Example analysis use cases
└── examples/               # Folder with example inputs and outputs
    ├── rooftop_.jpg        # Sample rooftop image (input for analysis)
    └── analysis_.json      # Sample analysis result (output from analyzer)
```

## 🌱 Environmental Impact

This tool supports India's ambitious renewable energy goals:
- **Net Zero by 2070**: Contributing to India's climate commitments
- **Renewable Energy Targets**: Supporting solar capacity expansion
- **CO₂ Offset Calculations**: Environmental impact quantification

## 🚨 Troubleshooting

| Issue | Solution |
|-------|----------|
| **API Error: 404** | Try different AI model from dropdown |
| **API Error: 402** | Daily limit exceeded, wait 24 hours or add credits |
| **Image analysis failed** | Ensure clear rooftop image, check supported formats |
| **CV works without API** | Computer vision functions independently of API |


## 📄 License

Educational project developed for Solar Industry AI Assistant internship assessment.
This project is licensed under the MIT License. See the [`LICENSE`](LICENSE) file for details.

## 👨‍💻 Author

**[Priyanshu Kumar](https://github.com/SyntaxError-Natsu)** - Solar Industry AI Assistant Candidate
- **Email**: Priyanshu.pp8@gmail.com

## 🔗 Links

- **🌐 Live Demo**: [Hugging Face Spaces](https://huggingface.co/spaces/Natsu-Error/Solar-Rooftop-Analyzer)
- **📚 Documentation**: [GitHub Repository](https://github.com/SyntaxError-Natsu/Solar-Rooftop-Analyzer)
- **📊 Technical Details**: [Implementation Guide](docs/implementation.md)
- **💡 Examples**: [Analysis Examples](docs/examples.md)

## 🤝 Contributing

This project is part of an internship assessment. For questions or suggestions:
1. Check the troubleshooting section
2. Review the technical documentation
3. Contact the author via email

---

*Built with ❤️ for India's renewable energy future*
