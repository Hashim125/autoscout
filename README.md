# ⚽ HashAI - Football Intelligence Report Generator

HashAI is an AI-powered football scouting and analysis platform that generates professional reports from match and player data. Built with Streamlit and powered by OpenAI/OpenRouter, it provides automated insights for coaches, analysts, and scouts.

## 🚀 Features

### 📊 **Report Generation**
- **Player Reports**: Detailed individual player analysis with technical, tactical, physical, and psychological insights
- **Match Reports**: Comprehensive match analysis with key events, trends, and standout performers
- **Opposition Reports**: Tactical analysis of opponent teams with actionable insights

### 🎯 **Smart Data Processing**
- **Column Normalization**: Automatically maps different data provider formats (Wyscout, StatsBomb, Opta, etc.)
- **Data Validation**: Comprehensive validation with quality warnings and error handling
- **Data Sanitization**: Removes sensitive information and cleans data automatically

### 📈 **Visualization Suggestions**
- **AI-Generated Code**: Suggests relevant matplotlib/mplsoccer visualizations
- **Code Safety**: Secure code execution with pattern detection and sandboxing
- **Multiple Models**: Support for various AI models (Llama, GPT, Claude, Gemini)

### 🎨 **Modern UI/UX**
- **Streaming Responses**: Real-time report generation with progress tracking
- **Responsive Design**: Clean, professional interface with custom styling
- **Advanced Settings**: Model selection, temperature control, and customization options

## 🏗️ Architecture

```
autoscout/
├── app.py                 # Main Streamlit application
├── app_improved.py        # Enhanced version with modular architecture
├── config/
│   └── settings.py        # Application configuration and constants
├── services/
│   └── openai_service.py  # OpenAI/LLM integration service
├── utils/
│   ├── visualization_utils.py  # Visualization and code execution utilities
│   ├── prompt_builder.py       # GPT prompt construction
│   └── validators.py           # Data and input validation
├── data/
│   └── sample_match.csv   # Sample data file
└── requirements.txt       # Python dependencies
```

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- OpenRouter API key

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd autoscout
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   # Create .env file
   echo "OPENROUTER_API_KEY=your_api_key_here" > .env
   ```

4. **Run the application**
   ```bash
   # Run the original version
   streamlit run app.py
   
   # Run the improved version
   streamlit run app_improved.py
   ```

## 📖 Usage Guide

### 1. **Upload Data**
- Upload a CSV file containing football match or player data
- Supported formats: Wyscout, StatsBomb, Opta, Impect, or custom formats
- File size limit: 50MB

### 2. **Select Report Type**
- **Player Report**: Analyze individual player performance
- **Match Report**: Comprehensive match analysis
- **Opposition Report**: Tactical analysis of opponent teams

### 3. **Configure Settings**
- Choose AI model (free and paid options available)
- Adjust creativity level (temperature)
- Enable/disable visualization suggestions

### 4. **Generate Report**
- Click "Generate Report" to start AI analysis
- Watch real-time streaming of the report
- Download results as text file

### 5. **Visualizations** (Optional)
- Review suggested visualization code
- Copy code to your own environment for execution
- Customize visualizations as needed

## 🔧 Configuration

### Environment Variables
```bash
OPENROUTER_API_KEY=your_api_key_here
```

### Supported Data Formats
The application automatically normalizes column names from various data providers:

| Provider | Team Column | Player Column | Position Column |
|----------|-------------|---------------|-----------------|
| Wyscout | Squad Name | Player Name | Position |
| StatsBomb | Team | Player | Position |
| Opta | Team Name | Player Name | Role |
| Custom | Team | Player | Pos |

### AI Models
- **Free Models**: Llama 3 70B, Gemini Pro, Claude 3 Haiku
- **Paid Models**: GPT-4o, GPT-4 Turbo

## 🛡️ Security Features

### Code Execution Safety
- **Pattern Detection**: Blocks dangerous code patterns
- **Sandboxed Execution**: Restricted environment for code execution
- **Timeout Protection**: Prevents infinite loops
- **Resource Limits**: Memory and CPU restrictions

### Data Protection
- **Input Sanitization**: Removes sensitive information
- **Column Mapping**: Preserves data privacy
- **Validation**: Comprehensive input validation

## 🧪 Testing

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest tests/ -v --cov=utils --cov=services
```

### Test Coverage
- Data validation functions
- Visualization utilities
- OpenAI service integration
- Prompt building logic

## 🚀 Performance Optimizations

### Caching
- **Streamlit Caching**: Service initialization and data processing
- **Response Caching**: Avoid redundant API calls
- **Model Caching**: Reuse model instances

### Memory Management
- **Data Chunking**: Process large datasets in chunks
- **Garbage Collection**: Automatic cleanup of temporary objects
- **Resource Monitoring**: Track memory usage

## 🔮 Future Enhancements

### Planned Features
- **PDF Export**: Direct PDF report generation
- **Batch Processing**: Multiple file processing
- **Custom Templates**: User-defined report templates
- **API Integration**: REST API for programmatic access
- **Database Support**: Persistent storage for reports
- **Real-time Collaboration**: Multi-user editing

### Technical Improvements
- **Docker Support**: Containerized deployment
- **CI/CD Pipeline**: Automated testing and deployment
- **Monitoring**: Application performance monitoring
- **Analytics**: Usage analytics and insights

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

### Code Style
- Follow PEP 8 guidelines
- Use type hints
- Add docstrings to functions
- Include error handling

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

### Common Issues
1. **API Key Error**: Ensure OPENROUTER_API_KEY is set correctly
2. **File Upload Error**: Check file format and size limits
3. **Column Mapping Issues**: Verify data format compatibility

### Getting Help
- Check the documentation
- Review error messages in the application
- Open an issue on GitHub
- Contact the development team

## 📊 Sample Data

The application includes sample data files for testing:
- `data/sample_match.csv`: Sample match data
- Additional sample files can be added to the `data/` directory

## 🔗 Links

- **OpenRouter**: https://openrouter.ai
- **Streamlit**: https://streamlit.io
- **mplsoccer**: https://mplsoccer.readthedocs.io
- **Documentation**: [Link to docs]

---

**Built with ❤️ for the football community**
