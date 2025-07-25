# Expense-Tracker

![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)
![Status](https://img.shields.io/badge/status-active-brightgreen.svg)

A clean, modern, and offline-first desktop application for tracking your daily expenses. Built with Python and CustomTkinter, this project focuses on simplicity, privacy, and giving you total control over your financial data.

---

## Key Features

* **Add Expenses:** Quickly add new expenses with an amount, category, and description.
* **View & Delete:** See a clear list of all your past expenses. Select and delete any entry with a single click.
* **Spending Analysis:** Get an instant overview of your spending habits with a simple breakdown by category, visualized with progress bars.
* **Monthly Budgeting:** Set a budget for any month and track your spending against it with a visual progress bar.
* **Modern GUI:** A clean and intuitive graphical user interface with both light and dark modes.
* **100% Offline:** Works entirely offline. Your data is stored locally and never leaves your computer.

---

## Application Preview

Here is a quick look at the different tabs in the application.
[Work in progress]
---

## 🚀 Getting Started

There are two ways to use this application: for non-programmers (easy way) and for developers.

### 1. For General Users (Easy Way)

If you don't have Python installed and just want to use the application, you can download the executable (`Expense-Tracker.exe`) file.

1.  Go to the [**Releases**](https://github.com/Bhavesh-exe/Expense-Tracker/releases) page of this repository.
2.  Under the latest release, click on `Expense-Tracker.exe` to download it.
3.  Double-click the downloaded file to run the application. That's it!

### 2. For Developers

If you have Python installed and want to run the code yourself, follow these steps.

#### Prerequisites

* Python 3.8 or newer. You can download it from [python.org](https://www.python.org/downloads/).

#### Installation

1.  **Clone the repository:**
    ```sh
    git clone [https://github.com/Bhavesh-exe/Expense-Tracker.git](https://github.com/Bhavesh-exe/Expense-Tracker.git)
    cd Expense-Tracker
    ```

2.  **Install the required library:**
    ```sh
    pip install customtkinter
    ```

3.  **Run the application:**
    ```sh
    python expense-tracker.py
    ```
    The application window should now appear on your screen!

---

## Why This Project?

This project was built to solve several key pain points with modern finance apps:

* ** Absolute Privacy:** Your financial data is stored locally on your machine in simple CSV files. No cloud, no servers, no risk of data breaches.
* ** No Fees, No Ads:** This app is completely free, forever. No hidden costs, no premium features, and no annoying ads.
* ** Simplicity and Focus:** A minimalist and efficient tool that focuses on the core tasks of logging expenses and understanding your spending habits without any distractions.

---

## File Structure

* `expense-tracker.py`: The main Python script containing all the application logic and GUI code.
* `expenses.csv`: The file where all your individual expense records are saved.
* `budgets.csv`: The file where your monthly budget information is stored.

*(These CSV files will be created automatically in the same directory as the script when you first run the application.)*
