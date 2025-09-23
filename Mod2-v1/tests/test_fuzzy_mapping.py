from app.models.schemas import Keyphrase
from app.services.mapping import map_keyphrases_to_elements

def test_fuzzy_mapping_contactform_and_servicesgrid():
    kps = [
        Keyphrase(text="обратный связь", lemma="обратный связь", confidence=0.8),
        Keyphrase(text="каталог услуга", lemma="каталог услуга", confidence=0.8),
    ]
    mappings = map_keyphrases_to_elements(kps, fuzzy_threshold=0.8)
    elems = [m.element for m in mappings]
    assert "ContactForm" in elems
    assert "ServicesGrid" in elems
