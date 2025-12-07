from commonfunctions import getfilelist
from configparser import ConfigParser
from pathlib import Path
from langchain_community.document_loaders import TextLoader, ObsidianLoader, UnstructuredHTMLLoader
from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
import pytesseract
from pdf2image import convert_from_path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
import re

config = ConfigParser()
config.read("assistantconfig.ini")

t = Path(config["DEFAULTS"]["vectorbasedatalocation"])
vectordatabasepath = Path(config["DEFAULTS"]["vectordatabasepath"])
model = config["DEFAULTS"]["ollamamodel"]
popplerpath = config["DEFAULTS"]["popplerpath"]
obsidianfilespath = config["DEFAULTS"]["notespath"]

def createpdfdocuments() -> None:
    for file in pdffiles:
        print(f"Loading: {file}")
        pages = convert_from_path(file, poppler_path=popplerpath) # converts pdf pages to images
        numberofpages = len(pages) 

        i = 0 # counter for page number
        for page in pages:
            pagecontents = pytesseract.image_to_string(page).replace("\n", " ") # converts text found inside image to string
            pagecontents = pagecontents.replace(" e ", " ") # Bullet points are sometimes recognized as stray e's so this gets rid of them 
            pdfdocs.append(Document(page_content=pagecontents, metadata={'source': file, 'total_pages' : numberofpages, "page_number": i})) # adds each page as a seperate document object with page number specification and source path metadata
            i+=1

def createtextfiledocuments() -> None:
    specialcharacter = r"[:+*&#;]"
    for file in txtfiles:
        textloader = TextLoader(file, autodetect_encoding=True) # Needs detect encoding otherwise certain files WILL raise the hellish Unicode Decode Error
        text = textloader.load()

        print(f"Loading: {text[0].metadata['source']}")
        newtext = re.sub(specialcharacter, "", text[0].page_content)
        textsplitter = RecursiveCharacterTextSplitter(separators=[".", "!"], chunk_size=500, chunk_overlap=1, length_function=len, is_separator_regex=False) # splitter object that will split giant string into 2000 character chunks 
        texts = textsplitter.split_text(newtext) # unpacks split text into list and gets rid of certain special characters
        # print(texts)
        for i in texts[:-2]:
            # print(i)
            txtdocs.append(Document(page_content=i, metadata={'path':file, 'length':len(i)})) # for chunk in the new list of split text assign metadata and convert to a document object

def createhtmldocuments() -> None: # Honestly this function may be scrapped, website files clog up the database and decrease the quality of repsonses unless more preprocessing is applied
    for file in htmlfiles:
        htmlloader = UnstructuredHTMLLoader(file)
        htmlcontent = htmlloader.load()
        print(f"Loading: {htmlcontent[0].metadata['source']}")
        htmlcontent[0].metadata["path"] = htmlcontent[0].metadata["source"]
        htmlcontent[0].page_content = htmlcontent[0].page_content.replace("\n", " ")
        htmldocs.append(htmlcontent[0])

print("") # makes console output 1 line down from the input bar for prettiness

# Obtain filenames and paths of every document to add to vectorstore
files_to_add = getfilelist(t)

# organize different file types into lists 
pdfdocs = []
txtdocs = []
htmldocs = []

htmlfiles = [i for i in files_to_add if i.endswith(".html")]
pdffiles = [i for i in files_to_add if i.endswith(".pdf")]
txtfiles = [i for i in files_to_add if i.endswith(".txt")]

# load obsidian notes into document objects
# obsidianloader = ObsidianLoader(obsidianfilespath)
# obsidiandocs = obsidianloader.load()
# for i in obsidiandocs:
#     print(f"Loading: {i.metadata["path"]}")

# load html documents
# createhtmldocuments()

# load pdf documents
# createpdfdocuments() 

# load txt documents
createtextfiledocuments() 

# combine docments into 1 big list
docs = txtdocs#pdfdocs + htmldocs + obsidiandocs
print(f"\nNumber of Documents: {len(docs)}")
print("-------------------------------------------------------------------------\n")
# ids = []
# for i in range(len(docs)):
#     ids.append(str(i))

# embed and add to vector store
# InMemoryVectorStore
# vector_store = InMemoryVectorStore(OllamaEmbeddings(model="llama3.1:8b"))
# # print(docs)
# vector_store.add_documents(documents=docs)
# vector_store.dump(r"C:\Users\geoha\Desktop\vectorestore")

# if __name__ == "__main__":
#     try:
        # initialize ollama embedding function for converting document objects into vectors
embeddings = OllamaEmbeddings(model=model)

# Chroma Instantiation
vectordatabase = Chroma.from_documents(
    docs,
    embeddings,
    collection_name="trainingdata",
    persist_directory=r"C:\Users\geoha\Desktop\vectorbase"
)

# Add documents to vector database
# vectordatabase.add_documents(documents=docs, ids=[str(i) for i in range(len(docs))]) 
# vectordatabase.persist()
        # Test Query to generate folder with header files, needed to access this database again in a new session
        # print("Performing Test Query")
        # query = "What do alpha brainwaves mean?"
        # context = vectordatabase.similarity_search_by_vector(embedding=embeddings.embed_query(query), k=1)

    # except Exception as e:
    #     print(f"Creation of Vector Database failed: {e}")