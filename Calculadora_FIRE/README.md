# 🔥 Calculadora FIRE - Módulo Odoo

![Odoo](https://img.shields.io/badge/Odoo-19.0-714B67?style=flat-square&logo=odoo)
![Status](https://img.shields.io/badge/Status-Pronto-success?style=flat-square)
![License](https://img.shields.io/badge/License-LGPL--3-green?style=flat-square)

## 📋 Sobre o Módulo

**Calculadora FIRE** é um snippet para o Website Builder do Odoo que permite aos visitantes calcularem sua **Independência Financeira** baseado no movimento **FIRE** (Financial Independence, Retire Early).

### 🎯 O que a calculadora oferece:

#### 🔥 **FIRE Tradicional** - Independência Total
- Calcula valor necessário para cobrir 100% dos gastos com investimentos
- Baseado na regra dos 4% (SWR - Safe Withdrawal Rate)
- Projeção de tempo para atingir a meta
- Barra de progresso visual

#### ☕ **Barista FIRE** - Liberdade Parcial
- Calcula quanto você precisa se quiser trabalhar meio período
- Permite configurar % dos gastos cobertos por investimentos
- Ideal para quem quer flexibilidade sem parar totalmente de trabalhar
- Mostra renda part-time necessária

#### 🌊 **Coast FIRE** - Piloto Automático
- Ponto onde você pode parar de aportar e deixar juros compostos trabalharem
- Calcula quanto seu patrimônio atual crescerá até a aposentadoria
- Mostra projeção de crescimento automático

### ✨ Recursos Avançados:

- 📊 **Cálculos em tempo real** - Resultados instantâneos ao alterar valores
- 💾 **Salva preferências** - LocalStorage mantém seus dados entre sessões
- 🎚️ **Configurações avançadas** - Ajuste retorno, inflação, SWR, gastos futuros
- 🏆 **Badges de conquista** - Marcos de R$ 250K, 500K e 1M
- ⚠️ **Validações inteligentes** - Alertas contextuais sobre taxa de poupança, SWR, retorno
- 📱 **100% Responsivo** - Funciona perfeitamente em mobile e desktop
- 🎨 **Visual moderno** - Interface limpa com gradientes e animações

---

## 🚀 Instalação

### 1. Instalar o módulo

```bash
# Copie o diretório para addons do Odoo
cp -r Calculadora_FIRE /path/to/odoo/addons/

# Ou via git submodule
cd /path/to/odoo/addons/
git clone https://github.com/gzconsultoria/ODOO_Modules.git
```

### 2. Atualizar lista de apps

1. Acesse Odoo
2. Ative o **Modo Desenvolvedor**
3. Apps → Atualizar Lista de Apps
4. Procure por "Calculadora FIRE"
5. Clique em **Instalar**

---

## 📖 Como Usar

### No Website Builder:

1. **Website** → Ir para Website
2. Clique em **Editar**
3. Na barra lateral, procure por **"Calculadora FIRE"** (ou aba "Dynamic Content")
4. **Arraste e solte** o snippet na página desejada
5. **Publique** a página

### Snippet funcionará:

- ✅ Em qualquer página do website
- ✅ Com múltiplas instâncias na mesma página
- ✅ Sem necessidade de configuração adicional
- ✅ Com todos os cálculos funcionando offline (client-side)

---

## 🎛️ Configurações Disponíveis

### Dados Básicos:
- Idade atual e idade de aposentadoria
- Gastos mensais e renda mensal
- Valor já investido e aportes mensais

### Configurações de Estratégia:
- **% de cobertura dos investimentos** (0-100%) - Para Barista FIRE
- **Ajuste de gastos futuros** (-10% a +10%) - Gastos podem aumentar/diminuir
- **Taxa de retirada (SWR)** (0-6%) - Quanto usar do patrimônio por ano
- **Retorno anual esperado** (0-30%)
- **Taxa de inflação** (0-10%)
- **Modo Real** - Liga/desliga ajuste por inflação

---

## 🔧 Detalhes Técnicos

### Arquitetura:
- **Frontend**: 100% JavaScript vanilla (sem dependências externas)
- **Cálculos**: Client-side para performance máxima
- **Storage**: LocalStorage para persistência de dados
- **UI Framework**: Bootstrap 5 (nativo do Odoo)
- **Template Engine**: QWeb (Odoo)

### Arquivos:
```
Calculadora_FIRE/
├── __init__.py                           # Módulo Python vazio
├── __manifest__.py                       # Manifest do módulo
├── static/
│   ├── src/
│   │   ├── js/
│   │   │   └── fire_calculator.js       # Lógica de cálculo
│   │   └── css/
│   │       └── fire_calculator.css      # Estilos customizados
│   └── description/
│       ├── icon.png                      # Ícone do módulo
│       └── index.html                    # Descrição HTML
└── views/
    └── snippets.xml                      # Template QWeb + registro
```

### Performance:
- ⚡ Cálculos < 10ms
- 💾 Peso total: ~15KB (JS + CSS)
- 🚀 Zero requisições ao servidor
- 📱 Otimizado para mobile

---

## 🧮 Fórmulas Utilizadas

### FIRE Tradicional:
```
Meta = Gastos Anuais Futuros / Taxa de Retirada (SWR)
Exemplo: R$ 60.000/ano ÷ 4% = R$ 1.500.000
```

### Coast FIRE:
```
Valor Necessário = Meta FIRE / (1 + retorno)^anos
```

### Barista FIRE:
```
Meta = (Gastos × % Cobertura) / SWR
Renda Part-time = Gastos × (1 - % Cobertura)
```

### Tempo para Meta (n):
```
n = log((FV × i + PMT) / (PV × i + PMT)) / log(1 + i)
Onde: FV=meta, PV=valor atual, PMT=aporte, i=retorno mensal
```

---

## 🎨 Customização

### Alterar cores:
Edite `/static/src/css/fire_calculator.css`:

```css
.progress-bar {
    background: linear-gradient(90deg, #SEU_COR 0%, #SUA_COR 100%);
}
```

### Ajustar valores padrão:
Edite `/views/snippets.xml` e altere os `value=""` dos inputs.

### Adicionar novos cálculos:
Edite `/static/src/js/fire_calculator.js` na função `recalc()`.

---

## 📊 Exemplos de Uso

### Cenário 1: Jovem Investidor
- 25 anos, quer se aposentar aos 45
- Gasta R$ 4.000/mês, ganha R$ 8.000
- Já tem R$ 50.000, aporta R$ 3.000/mês
- **Resultado**: Atingirá FIRE em ~13 anos

### Cenário 2: Profissional Estabelecido
- 40 anos, quer se aposentar aos 55
- Gasta R$ 10.000/mês, ganha R$ 20.000
- Já tem R$ 500.000, aporta R$ 7.000/mês
- **Resultado**: Já atingiu Coast FIRE, pode reduzir aportes

### Cenário 3: Barista FIRE
- 35 anos, quer liberdade aos 45
- Gasta R$ 6.000/mês, cobre 60% com investimentos
- Já tem R$ 300.000, aporta R$ 4.000/mês
- **Resultado**: Precisará de R$ 2.400/mês de trabalho leve

---

## 🐛 Troubleshooting

**Snippet não aparece no editor:**
- Verifique se o módulo está instalado
- Limpe cache do navegador
- Recarregue a página do editor

**Cálculos não atualizam:**
- Verifique o console do navegador (F12)
- Confirme que o JavaScript está carregado
- Teste em modo anônimo (sem extensions)

**Valores estranhos:**
- Verifique se as idades são válidas
- Confirme que gastos mensais > 0
- Ajuste o SWR se estiver muito alto/baixo

---

## 🤝 Contribuindo

Sugestões de melhorias são bem-vindas! Abra uma issue ou PR no GitHub.

---

## 👨‍💻 Autor

**Geovane Zomer**  
GZ Consultoria  
📧 geovane.zomer@gmail.com  
🌐 [gzconsultoria.com.br](https://gzconsultoria.com.br)

---

## 📝 Licença

LGPL-3 - Livre para uso e modificação
