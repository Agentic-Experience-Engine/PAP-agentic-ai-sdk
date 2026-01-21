from kafka import KafkaConsumer
import json

from langchain_ollama.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

from core.llm import get_default_chat_model
def consume_search_events():

    llm = get_default_chat_model()

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are an data analyst for an e-commerce platform. Your job is to interpret the search input and provide a concise, one-sentence summary of the query.",
            ),
            ("human", "Search event: {event_data}"),
        ]
    )

    chain = prompt | llm

    searchConsumer = KafkaConsumer(
        "dev.amazon-clone.user-searches",
        bootstrap_servers=["localhost:29092"],
        group_id="search-agent-group-3",
        # This helps decode the message from bytes to a string
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    )

    print("Consumer is listening for messages on 'dev.amazon-clone.user-searches'...")

    # A consumer is like an iterable, we can loop over it forever
    for message in searchConsumer:
        # message.value is the data we sent from our Next.js app
        print(f"Received message: {message.value}")

        response = chain.invoke({"event_data": message.value})
        print(f"AI Analysis: {response.content}")
