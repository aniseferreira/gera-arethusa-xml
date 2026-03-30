import streamlit as st
import re
import xml.etree.ElementTree as ET
from datetime import datetime
import pandas as pd

# Configuração da Página
st.set_page_config(page_title="Arethusa XML Skeleton Generator", layout="wide")

def generate_skeleton_xml(text_block, annotator_name, annotator_email):
    # Cabeçalho Fixo conforme seu modelo
    root = ET.Element("treebank")
    root.set("xmlns:saxon", "http://saxon.sf.net/")
    root.set("xml:lang", "grc")
    root.set("version", "1.5")
    root.set("direction", "ltr")
    root.set("format", "smyth3")

    # Data atual
    date_node = ET.SubElement(root, "date")
    date_node.text = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')

    # Bloco de Anotadores (Mantendo a estrutura do seu exemplo)
    uris = [
        "http://github.com/latin-language-toolkit/arethusa",
        "http://services2.perseids.org/llt/segtok",
        "http://github.com/latin-language-toolkit/arethusa"
    ]
    for uri in uris:
        ann = ET.SubElement(root, "annotator")
        ET.SubElement(ann, "short")
        ET.SubElement(ann, "name")
        ET.SubElement(ann, "address")
        ET.SubElement(ann, "uri").text = uri

    # Anotador Principal (Usuário)
    ann_user = ET.SubElement(root, "annotator")
    ET.SubElement(ann_user, "short").text = annotator_name.split()[0].lower() if annotator_name else ""
    ET.SubElement(ann_user, "name").text = annotator_name
    ET.SubElement(ann_user, "address").text = annotator_email
    ET.SubElement(ann_user, "uri").text = f"http://data.perseus.org/sosol/users/{annotator_name.split()[0].lower() if annotator_name else 'user'}"

    # Processamento das Sentenças
    lines = [line.strip() for line in text_block.split('\n') if line.strip()]
    
    for i, line in enumerate(lines, 1):
        # Remove número inicial se existir (ex: "1 ἐγὼ...")
        clean_line = re.sub(r'^\d+\s+', '', line)
        tokens = re.findall(r"[\w\u0370-\u03FF\u1F00-\u1FFF]+|[.,;:·!?]", clean_line)
        
        sentence = ET.SubElement(root, "sentence", 
                                 id=str(i), 
                                 document_id="urn:cts:greekLit:arethusa.skeleton", 
                                 subdoc=f"1-{i}", 
                                 span="")
        
        # Primeiro Word ID=1 é o número da linha para manter seu padrão
        ET.SubElement(sentence, "word", id="1", form=str(i), lemma="", postag="", relation="", sg="", head="")
        
        # Tokens reais começando do ID 2
        for j, token in enumerate(tokens, 2):
            # Lógica para pontuação final automática
            is_punct = token in [".", "·", ";", "!", "·"]
            rel = "AuxK" if is_punct else ""
            head = "0" if is_punct else ""
            
            ET.SubElement(sentence, "word", 
                          id=str(j), 
                          form=token, 
                          lemma="", 
                          postag="", 
                          relation=rel, 
                          sg="", 
                          head=head)

    # Transformar em string formatada
    return ET.tostring(root, encoding='UTF-8', xml_declaration=True)

# Interface Streamlit
st.title("🏛️ Gerador de Esqueleto XML Arethusa")
st.markdown("### Insira as sentenças (uma por linha) para gerar o arquivo XML com atributos vazios.")

with st.sidebar:
    st.header("Dados do Anotador")
    name = st.text_input("Nome:", value="Anise Ferreira")
    email = st.text_input("E-mail:", value="anise.a@gmail.com")

input_text = st.text_area("Sentenças Gregas:", height=300, placeholder="1 ἐγὼ δ ' ἔσοπτρον εἴην...\n2 ἐγὼ χιτὼν γενοίμην...")

# ... (todo o resto do código acima)

if st.button("GERAR XML 🚀"):
    if txt_area:
        # 1. Gera o XML (lógica que já temos)
        result = generate_xml(txt_area, u_name, u_email)
        
        # 2. Mostra o botão de download (indentado dentro do if button)
        st.download_button(
            label="📥 Baixar XML para o Perseids",
            data=result,
            file_name="skeleton.xml",
            mime="application/xml",
            use_container_width=True
        )
        
        st.success("XML criado! Veja a prévia dos tokens abaixo:")

        # --- AQUI ENTRA O PANDAS PARA A TABELA ---
        # Criamos uma lista de dicionários rápida para o Pandas ler
        preview_data = []
        linhas = [l.strip() for l in txt_area.split('\n') if l.strip()]
        for linha in linhas:
            tokens = re.findall(r"[\w\u0370-\u03FF\u1F00-\u1FFF]+|[.,;:·!?]", linha)
            for t in tokens:
                preview_data.append({"Palavra": t, "Lemma": "", "Postag": ""})
        
        df = pd.DataFrame(preview_data)
        st.table(df) # Isso desenha a tabela na tela
        # -----------------------------------------
        
    else:
        st.error("Insira o texto antes de gerar.")
