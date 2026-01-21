# rag_struct/core.py
from typing import Iterable, Dict, Any, List
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel

SYSTEM_PROMPT = """You are an AI assistant for an e-commerce platform.
Use ONLY the given context to answer.
If the answer is not in the context, say you don't know instead of guessing.
Be concise and helpful.
"""

def _format_docs(docs: List[Document]) -> str:
    parts = []
    for i, d in enumerate(docs):
        parts.append(f"[{i+1}] {d.page_content}")
    return "\n\n".join(parts)

class RAG:
    def __init__(
        self,
        *,
        openai_api_key: str,
        openai_base_url: str | None = None,
        embedding_model: str = "text-embedding-3-large",
        chat_model: str = "gpt-4.1-mini",
        persist_directory: str = "./.rag_db",
        collection_name: str = "agentic_rag",
        top_k: int = 5,
    ):
        emb_kwargs = {}
        llm_kwargs = {}

        if openai_base_url:
            emb_kwargs["base_url"] = openai_base_url
            llm_kwargs["base_url"] = openai_base_url

        self.embeddings = OpenAIEmbeddings(
            api_key=openai_api_key,
            model=embedding_model,
            **emb_kwargs,
        )

        self.vs = Chroma(
            collection_name=collection_name,
            embedding_function=self.embeddings,
            persist_directory=persist_directory,
        )

        self.llm = ChatOpenAI(
            api_key=openai_api_key,
            model=chat_model,
            temperature=0.2,
            **llm_kwargs,
        )

        self.retriever = self.vs.as_retriever(search_kwargs={"k": top_k})
        self.chain = self._build_chain()

    def _build_chain(self):
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", SYSTEM_PROMPT),
                (
                    "human",
                    "Context:\n{context}\n\n"
                    "Question: {question}\n\n"
                    "If the context is insufficient, say you don't know.",
                ),
            ]
        )

        setup: RunnableParallel = RunnableParallel(
            context=self.retriever | _format_docs,
            question=RunnablePassthrough(),
        )

        return setup | prompt | self.llm

    def _chunk(
        self,
        texts: Iterable[str],
        metadatas: Iterable[Dict[str, Any]] | None = None,
        chunk_size: int = 800,
        chunk_overlap: int = 200,
    ) -> List[Document]:
        texts = list(texts)
        metadatas = list(metadatas) if metadatas is not None else [{} for _ in texts]

        docs = [
            Document(page_content=t, metadata=meta or {})
            for t, meta in zip(texts, metadatas)
        ]

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        return splitter.split_documents(docs)

    def ingest(
        self,
        texts: Iterable[str],
        metadatas: Iterable[Dict[str, Any]] | None = None,
        *,
        chunk_size: int = 800,
        chunk_overlap: int = 200,
    ) -> int:
        chunks = self._chunk(
            texts=texts,
            metadatas=metadatas,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

        if not chunks:
            return 0

        self.vs.add_documents(chunks)
        self.vs.persist()
        return len(chunks)

    def ask(self, question: str) -> Dict[str, Any]:
        resp = self.chain.invoke(question)
        return {"answer": resp.content}
