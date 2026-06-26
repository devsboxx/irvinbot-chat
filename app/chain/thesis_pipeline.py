from langchain_core.output_parsers import StrOutputParser
from typing import AsyncIterator

from app.chain.thesis_prompts import build_section_prompt, SECTIONS
from app.llm.providers import get_llm


def _build_chain(key: str):
    section = SECTIONS[key]
    return build_section_prompt(section["instruction"]) | get_llm() | StrOutputParser()


async def generate_section(key: str, objeto: str, datos: str) -> str:
    chain = _build_chain(key)
    return await chain.ainvoke({"objeto": objeto, "datos": datos})


async def stream_section(key: str, objeto: str, datos: str) -> AsyncIterator[str]:
    chain = _build_chain(key)
    async for chunk in chain.astream({"objeto": objeto, "datos": datos}):
        yield chunk
