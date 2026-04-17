import express from 'express';
import { createServer } from 'http';
import { Server } from 'socket.io';
import cors from 'cors';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const httpServer = createServer(app);
const io = new Server(httpServer, {
  cors: {
    origin: "*",
    methods: ["GET", "POST"]
  }
});

app.use(cors());
app.use(express.json());

// Servir arquivos estáticos do frontend
app.use(express.static(path.join(__dirname, '../frontend')));

// Rotas para as visões
app.get('/medico', (req, res) => {
  res.sendFile(path.join(__dirname, '../frontend/medico.html'));
});

app.get('/surdo', (req, res) => {
  res.sendFile(path.join(__dirname, '../frontend/surdo.html'));
});

// Socket.IO - Comunicação em tempo real
io.on('connection', (socket) => {
  console.log('👤 Usuário conectado:', socket.id);
  
  // Surdo enviando gesto reconhecido
  socket.on('gesto_reconhecido', (data) => {
    console.log('🤟 Gesto do surdo:', data.texto);
    io.emit('resposta_gesto', data);
  });
  
  // Médico enviando fala
  socket.on('fala_medico', (data) => {
    console.log('🎤 Médico disse:', data.texto);
    io.emit('resposta_fala', data);
  });
  
  socket.on('disconnect', () => {
    console.log('👋 Usuário desconectado:', socket.id);
  });
});

const PORT = 3000;
httpServer.listen(PORT, () => {
  console.log(`\n✅ Servidor rodando em http://localhost:${PORT}`);
  console.log(`👨‍⚕️ Visão do Médico: http://localhost:${PORT}/medico`);
  console.log(`🦻 Visão do Surdo: http://localhost:${PORT}/surdo\n`);
});