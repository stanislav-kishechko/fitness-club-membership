# Fitness Club Membership Service

## About This Project

### What is it?

The Fitness Club Membership Service is an online membership management system designed to modernize and automate how fitness clubs handle their memberships. It replaces manual, spreadsheet-based tracking with a comprehensive digital solution.

### Why do we need it?

Traditional fitness clubs face several challenges:
- **Manual tracking:** Staff manage memberships using spreadsheets and cash, which is time-consuming and error-prone
- **Missed renewals:** Members forget to renew, leading to lost revenue
- **Confused status tracking:** Hard to know who's active, frozen, or expired
- **Payment delays:** Members must visit the front desk to pay, creating bottlenecks
- **Limited visibility:** Administrators lack real-time insights into membership status

### What does it solve?

This system provides:
- **Online self-service:** Members can purchase, renew, freeze, and cancel memberships from anywhere
- **Automated payments:** Secure online payments through Stripe
- **Real-time notifications:** Staff receive instant Telegram alerts about purchases, expirations, and payments
- **Automatic tracking:** The system monitors membership status and sends expiration reminders
- **Auto-renewal:** Optional automatic membership renewal to prevent lapses
- **Upgrade flexibility:** Members can upgrade their plans mid-term with prorated pricing

## Key Features

- **Membership Management:** Purchase, renew, freeze, resume, cancel, and upgrade memberships
- **Multiple Plan Tiers:** Basic, Standard, and Premium membership options
- **Secure Payments:** Integrated Stripe payment processing
- **Smart Notifications:** Telegram alerts for staff about important events
- **Automated Reminders:** System sends notifications 7, 3, and 1 day before expiration
- **Flexible Freezing:** Members can pause memberships for up to 30 days
- **API-First Design:** Fully functional through browsable API interface

---

## Getting Started Guide (For Non-Technical Users)

This guide will help you run the Fitness Club Membership Service on your computer, even if you don't have technical experience.

## Prerequisites

Before running the project, you need to install two programs:

### 1. Docker Desktop

**What is it?** Docker is a program that allows you to run applications in special containers without worrying about setting up the environment.

**Where to download:**
- For Windows & Mac: [https://www.docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)
- For Linux: Follow instructions on the official Docker website

**How to install:**
1. Download the installation file from the website
2. Run the downloaded file
3. Follow the on-screen instructions
4. Restart your computer after installation

### 2. Git

**What is it?** Git is a program for working with project code.

**Where to download:**
- For all operating systems: [https://git-scm.com/downloads](https://git-scm.com/downloads)

**How to install:**
1. Download the installation file
2. Run it
3. During installation, you can simply click "Next" (all default settings will work)

## Downloading the Project

1. **Open Terminal (Command Prompt):**
   - **Windows:** Press `Win + R`, type `cmd`, and press Enter
   - **Mac:** Press `Cmd + Space`, type `Terminal`, and press Enter
   - **Linux:** Press `Ctrl + Alt + T`

2. **Navigate to the folder where you want to save the project:**
   ```bash
   cd Desktop
   ```
   *(This example will save the project to your Desktop)*

3. **Download the project:**
   ```bash
   git clone <repository-link>
   ```
   *(Replace `<repository-link>` with the actual link provided to you)*

4. **Navigate to the project folder:**
   ```bash
   cd fitness-club-membership
   ```
   *(The folder name may differ - use your project's name)*

## Configuration Before Launch

### Create a Secret Data File

There's a file called `.env.sample` in the project folder - this is a template for your settings.

1. **Copy the `.env.sample` file and name the copy `.env`:**
   - **Windows:** In File Explorer, find the file, right-click → Copy → Paste → Rename to `.env`
   - **Mac/Linux:** In terminal, execute:
     ```bash
     cp .env.sample .env
     ```

2. **Open the `.env` file in a text editor** (Notepad, TextEdit, VS Code)

3. **Fill in the required data:**
   - `STRIPE_SECRET_KEY` - your Stripe API key (payment system)
   - `TELEGRAM_BOT_TOKEN` - your Telegram bot token
   - `TELEGRAM_CHAT_ID` - chat ID for receiving notifications
   - Other settings can be left as default

### How to Get Required Credentials

#### Stripe Setup:
1. Go to [https://stripe.com](https://stripe.com) and create an account
2. Select a test country (e.g., USA) - **use test mode only**
3. Navigate to Developers → API Keys
4. Copy the "Secret key" (starts with `sk_test_`)
5. **Important:** You don't need to activate your account; work with test data only

#### Telegram Bot Setup:
1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send `/newbot` command
3. Follow instructions to create your bot
4. Copy the token provided (looks like `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)
5. Create a group chat and add your bot to it
6. To get the chat ID, send a message to the group, then visit:
   ```
   https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
   ```
   Replace `<YOUR_BOT_TOKEN>` with your actual token
7. Look for `"chat":{"id":-123456789}` in the response

## Running the Project

### Make Sure Docker is Running

1. Open Docker Desktop
2. Wait until the program fully starts (green icon at the bottom)

### Launch the Project

In the terminal, while in the project folder, execute:

```bash
docker-compose up
```

**What will happen:**
- Docker will start downloading necessary components (this may take 5-10 minutes on first launch)
- You'll see a lot of text in the terminal - this is normal
- When everything is ready, you'll see messages indicating successful launch

### Verify It's Working

Open your browser and go to:
```
http://localhost:8000
```

If you see the API page - congratulations, everything works! 🎉

## How to Stop the Project

1. Return to the terminal window where the project is running
2. Press `Ctrl + C` (on Mac also `Ctrl + C`)
3. Wait for all services to fully stop

Alternatively, you can execute:
```bash
docker-compose down
```

## Useful Commands

### Restart the Project from Scratch
```bash
docker-compose down
docker-compose up --build
```

### View Logs (if something isn't working)
```bash
docker-compose logs
```

### View Logs for a Specific Service
```bash
docker-compose logs <service-name>
```
Where `<service-name>` can be: `web`, `db`, `redis`, `celery`, etc.

### Access the Database
PostgreSQL database is accessible on port `5432`

## Troubleshooting

### Problem: "docker: command not found"
**Solution:** Docker is not installed or not running. Check if Docker Desktop is installed and running.

### Problem: "Port already in use"
**Solution:** The port is already being used by another program. Stop other programs or change the port in `docker-compose.yml`.

### Problem: Project won't start
**Solution:**
1. Make sure the `.env` file is created and filled in
2. Verify all secret keys are correct
3. Try restarting Docker Desktop
4. Execute `docker-compose down` then `docker-compose up --build`

### Problem: Telegram notifications aren't working
**Solution:**
1. Check that `TELEGRAM_BOT_TOKEN` is correct
2. Make sure the bot is added to the chat
3. Verify `TELEGRAM_CHAT_ID` is correct
4. Ensure the bot has permission to send messages in the group

### Problem: Stripe payments aren't working
**Solution:**
1. Verify you're using the test API key (starts with `sk_test_`)
2. Check that `STRIPE_SECRET_KEY` in `.env` is correct
3. Make sure you're using test card numbers from [Stripe's testing documentation](https://stripe.com/docs/testing)

### Problem: Database connection errors
**Solution:**
1. Make sure the database container is running: `docker-compose ps`
2. Check database credentials in `.env` file
3. Try restarting all containers: `docker-compose restart`

## Accessing API Documentation

After launching the project, Swagger documentation is available at:
```
http://localhost:8000/swagger/
```

Here you can view all available API endpoints and test them.

## Testing the System

### Test Card Numbers (Stripe Test Mode)

Use these test card numbers to simulate payments:
- **Successful payment:** `4242 4242 4242 4242`
- **Declined payment:** `4000 0000 0000 0002`
- Use any future expiration date, any 3-digit CVC, and any ZIP code

### Sample User Flow

1. Register a new user via `/users/` endpoint
2. Get authentication token via `/users/token/`
3. View available membership plans via `/plans/`
4. Purchase a membership via `/memberships/`
5. Complete payment through the Stripe checkout URL
6. Check your Telegram for notification
7. View your active membership via `/memberships/`

## Technical Stack

- **Backend Framework:** Django & Django REST Framework
- **Database:** PostgreSQL
- **Task Queue:** Celery or Django-Q
- **Message Broker:** Redis
- **Payment Processing:** Stripe API
- **Notifications:** Telegram Bot API
- **Authentication:** JWT (JSON Web Tokens)
- **Containerization:** Docker & Docker Compose

## Support

If you encounter any problems, reach out to the development team through:
- GitHub Issues in the project repository
- Your corporate chat
- Project documentation

## Important Notes

- **Test Mode Only:** This project uses Stripe's test mode, so all payments are simulated. No real money will be charged.
- **Security:** Never commit the `.env` file to version control. It contains sensitive credentials.
- **Data Privacy:** Keep all user data secure and comply with relevant data protection regulations.

## License

This project is developed for educational purposes as part of a team project assignment.

---

**Version:** 1.0.0
**Last Updated:** January 2026
**Maintained by:** Your Development Team
