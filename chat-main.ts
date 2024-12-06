// chatModel.ts

import { Schema, model } from 'mongoose';
import axios from 'axios';
import readline from 'readline';

// Interfaces
export enum Role {
    SYSTEM = 'system',
    USER = 'user',
    ASSISTANT = 'assistant',
}

export enum PaymentMethod {
    ACH = 'ACH',
    CARD = 'CARD',
}

export interface ChatMessage {
    role: Role;
    content: string;
}

export interface PaymentParams {
    amount: string | null;
    frequency: string | null;
    period: string | null;
    start_date: string | null;
    payment_method: PaymentMethod;
}

const { CohereClientV2 } = require('cohere-ai');

const cohere = new CohereClientV2({
  token: 'auaYNw33GagLljWAKVy4ttxwvjHS6sPOfvKEi03E',
});

const chatSchema = new Schema<ChatMessage>({
    role: {
        type: String,
        required: true,
        enum: Object.values(Role),
    },
    content: {
        type: String,
        required: true,
    },
});

const paymentParamsSchema = new Schema<PaymentParams>({
    amount: String,
    frequency: String,
    period: String,
    start_date: String,
    payment_method: {
        type: String,
        enum: Object.values(PaymentMethod),
        default: PaymentMethod.ACH,
    },
});

const chatHistory: ChatMessage[] = [
    {
        role: Role.SYSTEM,
        content: '...',
    }
];

function isPaymentResponse(chatbotResponse: string): boolean {
    const paymentKeywords = ['amount', 'frequency', 'method'];
    return paymentKeywords.every(keyword => chatbotResponse.toLowerCase().includes(keyword.toLowerCase()));
}

function extractPaymentDetails(chatbotResponse: string): PaymentParams {
    const params: PaymentParams = {
        amount: null,
        frequency: null,
        period: null,
        start_date: null,
        payment_method: PaymentMethod.ACH,
    };

    const amountMatch = chatbotResponse.match(/[\$]?([\d,]+(?:\.\d{2})?)/);
    if (amountMatch) {
        params.amount = amountMatch[1].replace(',', '');
    }

    const frequencyMatch = chatbotResponse.match(/(SINGLE|MONTH|MONTHS|WEEKS|WEEK|FORTNIGHTS|FORTNIGHT)/i);
    if (frequencyMatch) {
        params.frequency = frequencyMatch[1].toUpperCase();
    }

    const periodMatch = chatbotResponse.match(/(\d+)\s?(MONTH|MONTHS|WEEKS|WEEK|FORTNIGHTS|FORTNIGHT|PAYMENTS)/i);
    if (periodMatch) {
        params.period = `${periodMatch[1]} ${periodMatch[2].toUpperCase()}`;
    }

    const dateMatch = chatbotResponse.match(/(\d{4}-\d{2}-\d{2})/);
    if (dateMatch) {
        params.start_date = dateMatch[1];
    }

    if (/ACH/i.test(chatbotResponse)) {
        params.payment_method = PaymentMethod.ACH;
    } else if (/CARD/i.test(chatbotResponse)) {
        params.payment_method = PaymentMethod.CARD;
    }

    return params;
}

// Dummy API Request Function
async function dummyApiRequest(params: PaymentParams): Promise<string> {
    return "API under development. No payment link available.";
}

async function processUserInput(userInput: string, rl: readline.Interface, storedRequest: Partial<PaymentParams>) {
    console.log(`\n<User> :\n\n${userInput}`);

    if (userInput.toLowerCase() === 'q') {
        console.log(`\n<System>\n\nStored Request: ${JSON.stringify(storedRequest, null, 4)}\n`);
        if (Object.keys(storedRequest).length) {
            console.log("\n<System>\n\nSending API Request...");
            const paymentLink = await dummyApiRequest(storedRequest as PaymentParams);
            console.log(`\n<Maxy-Mind>\n\nHere is your payment link: ${paymentLink}\n`);
        }
        rl.close();
        return;
    }

    chatHistory.push({ role: Role.USER, content: userInput });

    const response = await cohere.chat({
        model: 'command-r-plus-08-2024',
        messages: chatHistory
    });

    const assistantReply = response.message.content[0].text;
    chatHistory.push({ role: Role.ASSISTANT, content: assistantReply });

    if (isPaymentResponse(assistantReply)) {
        const params = extractPaymentDetails(assistantReply);
        Object.assign(storedRequest, params);
    }

    console.log(`\n<Maxy-Mind> :\n\n${assistantReply}`);

    rl.prompt();
}

async function mainChatbot() {
    const storedRequest: Partial<PaymentParams> = {};

    chatHistory.push({ role: Role.USER, content: 'hi' });

    const response = await cohere.chat({
        model: 'command-r-plus-08-2024',
        messages: chatHistory
    });

    const assistantReply = response.message.content[0].text;
    chatHistory.push({ role: Role.ASSISTANT, content: assistantReply });

    console.log(`\n<Maxy-Mind> :\n\n${assistantReply}`);

    const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout,
        prompt: '\n<User> :\n\n'
    });

    rl.prompt();

    rl.on('line', (line) => {
        processUserInput(line, rl, storedRequest);
    });
}

mainChatbot();