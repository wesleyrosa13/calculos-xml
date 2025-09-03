## 📦 Automação para Cálculo de Custos em XML de NF-e

Script em **Python** para processar arquivos XML de notas fiscais, calcular custos finais dos produtos com **DIFAL**, **ICMS ST**, **IPI** e **Descontos** e gerar planilhas de forma automatizada.

---

## 🚀 Funcionalidades

- Lê arquivos XML de notas fiscais.
- Calcula valores com **DIFAL**, **ICMS ST**, **IPI** e **Descontos**.
- Gera planilhas automáticas.
- Move os XMLs processados para uma pasta organizada.
- Permite informar a alíquota e o fornecedor na hora da execução.

---

## 🛠️ Tecnologias Usadas

- Python 3
- [pandas](https://pandas.pydata.org/)
- [openpyxl](https://openpyxl.readthedocs.io/en/stable/)

---

## 📂 Estrutura de Pastas

```
.
├── main.py
├── README.md
├── XMLsEntrada/
├── XMLsProcessados/
└── Planilhas/
```
---

## ▶️ Como Usar

1. Instale as dependências:

    pip install pandas openpyxl

2. Coloque os arquivos XML dentro da pasta XMLsEntrada.

3. Rode o script:
    
    python main.py

4. Digite a alíquota DIFAL, caso deixe em branco, será utilizado 14% por padrão.

5. Confira a planilha gerada na pasta Planilhas.

---

## 📌 Autor

Desenvolvido por Wesley Rosa.
📍 Estudante de Gestão de TI, entrando no universo de programação e tentando aprender mais sobre.

## 🤝 Contribuições

Sugestões e melhorias são bem-vindas!  
Sinta-se à vontade para abrir uma issue ou enviar um pull request.
