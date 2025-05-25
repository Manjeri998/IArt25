# Student Academic Outcome Prediction - README

This project implements supervised learning techniques to predict student academic outcomes (Graduate, Dropout, or Enrolled) based on various student attributes using machine learning models.

## Project Overview

The project analyzes student data to predict academic outcomes using multiple machine learning algorithms including Decision Trees, Random Forest, Logistic Regression, Support Vector Machines, and K-Nearest Neighbors.

## Project Structure

```
Proj2/
├── data/
│   ├── train.csv              # Training dataset
│   ├── test.csv               # Test dataset
│   └── sample_submission.csv  # Sample submission format
└── src/
    └── student_outcome.ipynb  # Main Jupyter notebook
```

## Prerequisites

### Required Software
- Python 3.7 or higher
- Jupyter Notebook or JupyterLab
- pip (Python package installer)

### Required Python Libraries

Install the following packages using pip:

```bash
pip install numpy pandas matplotlib seaborn scikit-learn jupyter
```

Or install all dependencies at once:

```bash
pip install numpy pandas matplotlib seaborn scikit-learn jupyter math warnings time
```

## Installation and Setup

1. **Open the project** in your local machine

2. **Navigate to the project directory**:
   ```bash
   cd /path/to/Proj2
   ```

3. **Install required packages listed above**:

4. **Verify data files** are present in the `data/` directory:
   - `train.csv` - Training dataset with student features and target outcomes
   - `test.csv` - Test dataset for predictions
   - `sample_submission.csv` - Example submission format

## How to Run the Program

### Method 1: Using Jupyter Notebook

1. **Start Jupyter Notebook**:
   ```bash
   jupyter notebook
   ```

2. **Navigate to the project** in the Jupyter interface

3. **Open the notebook**:
   - Click on `src/student_outcome.ipynb`

4. **Run the notebook**:
   - Execute cells sequentially by pressing `Shift + Enter`
   - Or run all cells at once: `Cell → Run All`

### Method 2: Using JupyterLab

1. **Start JupyterLab**:
   ```bash
   jupyter lab
   ```

2. **Open the notebook** `src/student_outcome.ipynb`

3. **Execute the cells** as described above

### Method 3: Command Line Execution

```bash
jupyter nbconvert --to notebook --execute src/student_outcome.ipynb
```

## How to Use the Program

### Data Input

The program expects CSV files in the `data/` directory:

- **Training Data** (`train.csv`): Contains 38 columns including:
  - Student demographics (age, gender, marital status)
  - Academic information (previous qualifications, grades)
  - Course details (application mode, course type)
  - Performance metrics (curricular units, evaluations)
  - Economic indicators (unemployment rate, inflation, GDP)
  - **Target variable**: Academic outcome (Graduate/Dropout/Enrolled)

- **Test Data** (`test.csv`): Same features as training data but without the target variable

### Program Workflow

The notebook follows this structure:

1. **Data Loading and Exploration**
   - Loads training and test datasets
   - Displays basic statistics and data types
   - Checks for missing values

2. **Data Preprocessing**
   - Feature scaling using StandardScaler
   - Handling categorical variables
   - Data splitting for training and validation

3. **Model Implementation**
   - Decision Tree Classifier
   - Random Forest Classifier
   - Logistic Regression   
   - K-Nearest Neighbors

4. **Model Evaluation**
   - Cross-validation scores
   - Accuracy, precision, recall, F1-score
   - Confusion matrices
   - ROC curves and AUC scores

5. **Hyperparameter Tuning**
   - Grid search and randomized search
   - Model optimization

6. **Predictions and Results**
   - Final model predictions on test data
   - Performance comparison between models

### Customization Options

- **Modify hyperparameters**: Edit the parameter grids in the hyperparameter tuning sections
- **Add new models**: Import additional scikit-learn classifiers and follow the same pattern
- **Change evaluation metrics**: Modify the scoring functions in the evaluation sections
- **Adjust data preprocessing**: Modify the preprocessing pipeline as needed

## Expected Output

The program will generate:

1. **Data exploration results**: Statistics, visualizations, and data quality reports
2. **Model performance metrics**: Accuracy scores, confusion matrices, classification reports
3. **Visualizations**: ROC curves, feature importance plots, performance comparisons
4. **Predictions**: Final predictions on the test dataset
