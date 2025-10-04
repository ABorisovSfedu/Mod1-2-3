from app.services.chunker import make_chunks

def test_chunking_overlap_and_seq():
    sents = [f"Предложение {i}." for i in range(1, 11)]
    chunks = make_chunks("s1", sents, start_seq=1)
    assert chunks[0].seq == 1
    assert chunks[-1].seq == chunks[0].seq + len(chunks) - 1
    for i in range(1, len(chunks)):
        assert isinstance(chunks[i].overlap_prefix, str)