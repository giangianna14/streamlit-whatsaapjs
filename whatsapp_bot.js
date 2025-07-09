const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const fs = require('fs');

class WhatsAppBot {
    constructor() {
        this.client = new Client({
            authStrategy: new LocalAuth(),
            puppeteer: {
                headless: true,
                // executablePath: '/usr/bin/google-chrome-stable',
                // executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
                args: [
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--no-first-run',
                    '--no-zygote',
                    '--disable-gpu',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor'
                ]
            }
        });
        
        this.setupEventHandlers();
    }
    
    setupEventHandlers() {
        // Event ketika QR code siap
        this.client.on('qr', (qr) => {
            console.log('QR RECEIVED', qr);
            qrcode.generate(qr, { small: true });
            
            // Simpan QR code ke file untuk dibaca Streamlit
            fs.writeFileSync('qr_code.txt', qr);
        });
        
        // Event ketika bot siap
        this.client.on('ready', () => {
            console.log('WhatsApp bot is ready!');
            fs.writeFileSync('bot_status.txt', 'ready');
        });
        
        // Event ketika menerima pesan
        this.client.on('message', async (message) => {
            try {
                await this.handleMessage(message);
            } catch (error) {
                console.error('Error handling message:', error);
            }
        });
        
        // Event disconnected
        this.client.on('disconnected', (reason) => {
            console.log('Client was logged out', reason);
            fs.writeFileSync('bot_status.txt', 'disconnected');
        });
    }
    
    async handleMessage(message) {
        // Abaikan pesan dari grup dan status
        if (message.from.includes('@g.us') || message.from.includes('status@broadcast')) {
            return;
        }
        
        // Abaikan pesan dari bot sendiri
        if (message.fromMe) {
            return;
        }
        
        const phoneNumber = message.from.replace('@c.us', '');
        const messageText = message.body;
        
        console.log(`Received message from ${phoneNumber}: ${messageText}`);
        
        // Log pesan ke file untuk monitoring
        const logEntry = {
            timestamp: new Date().toISOString(),
            from: phoneNumber,
            message: messageText
        };
        
        // Append to log file
        const logData = fs.existsSync('message_logs.json') ? 
            JSON.parse(fs.readFileSync('message_logs.json', 'utf8')) : [];
        logData.push(logEntry);
        fs.writeFileSync('message_logs.json', JSON.stringify(logData, null, 2), 'utf8');
        
        // Proses pesan menggunakan chatbot logic
        const response = await this.processWithChatbot(messageText, phoneNumber);
        
        if (response) {
            await message.reply(response);
            
            // Log response
            const responseLog = {
                timestamp: new Date().toISOString(),
                to: phoneNumber,
                response: response
            };
            logData.push(responseLog);
            fs.writeFileSync('message_logs.json', JSON.stringify(logData, null, 2), 'utf8');
        }
    }
    
    async processWithChatbot(message, phoneNumber) {
        // Use proper Python environment for processing
        const { spawn } = require('child_process');

        return new Promise((resolve, reject) => {
            // Use Windows-style Python path for local dev
            const path = require('path');
            const pythonPath = path.join(__dirname, 'venv', 'Scripts', 'python.exe');
            const python = spawn(pythonPath, ['process_message.py', message, phoneNumber], {
                cwd: __dirname,
                env: { ...process.env, PYTHONIOENCODING: 'utf-8' }
            });

            let response = '';
            let errorOutput = '';

            python.stdout.on('data', (data) => {
                response += data.toString();
            });

            python.stderr.on('data', (data) => {
                errorOutput += data.toString();
            });

            python.on('close', (code) => {
                if (code === 0) {
                    resolve(response.trim());
                } else {
                    console.error('Python process error:', errorOutput);
                    resolve("Maaf, terjadi kesalahan sistem. Silakan coba lagi.");
                }
            });

            python.on('error', (error) => {
                console.error('Failed to start Python process:', error);
                resolve("Maaf, sistem sedang bermasalah. Silakan coba lagi nanti.");
            });
        });
    }
    
    async start() {
        await this.client.initialize();
    }
    
    async sendMessage(phoneNumber, message) {
        try {
            const chatId = phoneNumber + '@c.us';
            await this.client.sendMessage(chatId, message);
            return true;
        } catch (error) {
            console.error('Error sending message:', error);
            return false;
        }
    }
}

// Inisialisasi dan jalankan bot
const bot = new WhatsAppBot();
bot.start();

module.exports = WhatsAppBot;
