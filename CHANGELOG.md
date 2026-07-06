# Changelog

## v1.0.0 (2025-07-06)

### 🏗️ Infraestrutura
- Código reestruturado em pacote Python (`poopy_clicker/`) instalável via pip
- `pyproject.toml` com entry point (`poopy-clicker` command)
- GitHub Actions para build automático do .exe (Windows) em releases
- Inno Setup script para instalador do Windows com atalho no Menu Iniciar
- `install.sh` para Linux (venv + atalho no menu de apps)
- `flake.nix` para build via Nix (`nix run github:Cherievamp/poopy-clicker`)
- Save movido para `~/.poopy-clicker/save.json`
- Assets convertidos de .gif para .webp
- Save atômico (arquivo temporário + `os.replace`)

### 🎮 Jogo (vs fork original)
- **Reescrita completa**: Tkinter (~220 linhas) → PyQt6 (~4500 linhas em 12 módulos)
- Código monolítico (`poopy clicker.py`) dividido em **12 módulos**
- **18 tipos de goober** (comum, raro, épico, lendário, mítico) com animações individuais
- Goobers com **múltiplos hits** e barra de HP
- Chefes e goobers RGB
- Goobers irritados que perseguem o botão de clique
- Goobers especiais com eventos ao serem clicados
- **Loja de itens secreta** desbloqueável clicando em goobers (12 itens)
- **4 habilidades**: 🧹 Limpeza, ⚡ Frenesi, 🛡️ Escudo, 💰 Explosão de Moedas
- **Sistema de prestígio** com bônus percentual e essência
- **Sistema de combo** com multiplicador e decaimento progressivo
- **Sistema de eventos** aleatórios (bônus e penalidades) com duração variável
- **Sistema de missões** com progresso e recompensas
- **Sistema de conquistas** com notificações
- **Bestiário** catalogando todos os tipos de goober
- **Player de música** com suporte a MP3, OGG, WAV, FLAC, M4A, WMA
- **Auto-click** progressivo

### 🎨 Interface
- **8 temas** de interface (Dark, Light, Matrix, Blood, Ice, Gold, Neon, Slime)
- Diálogos responsivos (adaptam ao tamanho da tela como % do monitor)
- Menu principal dividido em categorias (Loja, Coleção, Progresso, Sistema)
- Loja secreta com descrições visíveis nos botões
- Notificações de conquistas não-modais
- Conquistas com nome em destaque e descrição em tom secundário

### 🔊 Áudio
- Gerenciador de som com QSoundEffect (SFX) e QMediaPlayer + QAudioOutput (música)
- 20+ efeitos sonoros
- Músicas em loop automático via sinal EndOfMedia
- Controle de volume individual para SFX e música
- Suporte a .mp3, .ogg, .wav, .flac, .m4a, .wma

### 🐛 Correções (vs código monolítico anterior)
- Goobers assustados não oscilam na borda (clamp de posição em vez de reversão de velocidade)
- Multi-hit sem freeze (removido `_move_cooldown`)
- Eventos com duração ajustada por tipo (bom/ruim lido de dicionário)
- Botões da loja com layout em QWidget + QLabels em vez de HTML em QPushButton
- EventBubble com fundo do tema atual em vez de preto fixo
- Diálogos não quebram ao fechar (try/except RuntimeError em widgets deletados)
- Fechar a aba goober não quebra a descrição da loja secreta (labels separadas)

### 👥 Créditos
- **Mafunky** (Cherievamp) — desenvolvimento principal, reescrita PyQt6, mecânicas do jogo, assets, sons, packaging, distribuição
- **Julia-Link** — criação do jogo original em Tkinter, conceito inicial, upgrades e save/load, contribuição no código PyQt6, ensinou bastante sobre a biblioteca

---

## Anterior (fork original — por Julia-Link)

### Última versão (`Julia-Link/poopy-clicker`)
- Jogo de cliques em **Tkinter** (~220 linhas, arquivo único)
- Clique para ganhar dinheiro
- 10 níveis de upgrade (2x a 1024x)
- Save/load via pickle
- README com links para builds Windows (py2exe.com) e Linux
- Ação de GitHub para build com PyInstaller (Windows)
- Interface cinza simples (Tkinter ttk)

