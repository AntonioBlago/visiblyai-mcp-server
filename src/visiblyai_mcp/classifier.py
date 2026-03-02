"""
Standalone Keyword Classifier (regex-only, zero external dependencies).

Extracted from unified_keyword_classifier.py for use in the MCP server package.
Classifies keywords by: intent, brand, funnel stage, topic, modifiers.
Supports German and English.
"""

import re
import hashlib
import logging
import threading
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)

MAX_KEYWORD_LENGTH = 500
CACHE_MAX_SIZE = 10000
CACHE_EVICTION_SIZE = 1000


# =============================================================================
# ENUMS
# =============================================================================

class IntentType(str, Enum):
    TRANSACTIONAL = "transactional"
    COMMERCIAL = "commercial"
    INFORMATIONAL = "informational"
    NAVIGATIONAL = "navigational"
    LOCAL = "local"


class BrandType(str, Enum):
    BRAND = "brand"
    BRAND_PRODUCT = "brand_product"
    COMPETITOR = "competitor"
    GENERIC = "generic"


class FunnelStage(str, Enum):
    TOFU = "tofu"
    MOFU = "mofu"
    BOFU = "bofu"


class ConversionPotential(str, Enum):
    HIGH = "high"
    MEDIUM_HIGH = "medium-high"
    MEDIUM = "medium"
    LOW = "low"


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class BrandClassification:
    type: BrandType
    confidence: float
    matched_brand: Optional[str] = None
    matched_product: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            "type": self.type.value,
            "confidence": self.confidence,
            "matched_brand": self.matched_brand,
            "matched_product": self.matched_product,
        }


@dataclass
class IntentClassification:
    type: IntentType
    confidence: float
    matched_patterns: List[str] = field(default_factory=list)
    conversion_potential: ConversionPotential = ConversionPotential.LOW

    def to_dict(self) -> Dict:
        return {
            "type": self.type.value,
            "confidence": self.confidence,
            "matched_patterns": self.matched_patterns,
            "conversion_potential": self.conversion_potential.value,
        }


@dataclass
class FunnelClassification:
    stage: FunnelStage
    confidence: float
    description: str

    def to_dict(self) -> Dict:
        return {
            "stage": self.stage.value,
            "confidence": self.confidence,
            "description": self.description,
        }


@dataclass
class ModifierClassification:
    has_year: bool = False
    has_location: bool = False
    has_price: bool = False
    has_comparison: bool = False
    has_question: bool = False
    has_best_of: bool = False
    has_how_to: bool = False
    has_negative: bool = False
    detected_modifiers: List[str] = field(default_factory=list)
    confidence_boost: float = 0.0

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class TopicClassification:
    primary_topic: str
    secondary_topics: List[str] = field(default_factory=list)
    confidence: float = 0.5

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class ClassificationResult:
    keyword: str
    brand: BrandClassification
    intent: IntentClassification
    funnel: FunnelClassification
    topic: TopicClassification
    modifiers: ModifierClassification
    overall_confidence: float
    conversion_score: int
    classification_method: str = "regex"
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict:
        return {
            "keyword": self.keyword,
            "brand": self.brand.to_dict(),
            "intent": self.intent.to_dict(),
            "funnel": self.funnel.to_dict(),
            "topic": self.topic.to_dict(),
            "modifiers": self.modifiers.to_dict(),
            "overall_confidence": self.overall_confidence,
            "conversion_score": self.conversion_score,
            "classification_method": self.classification_method,
            "timestamp": self.timestamp,
        }

    def to_flat_dict(self) -> Dict:
        return {
            "keyword": self.keyword,
            "brand_type": self.brand.type.value,
            "brand_confidence": self.brand.confidence,
            "matched_brand": self.brand.matched_brand,
            "matched_product": self.brand.matched_product,
            "intent_type": self.intent.type.value,
            "intent_confidence": self.intent.confidence,
            "conversion_potential": self.intent.conversion_potential.value,
            "funnel_stage": self.funnel.stage.value,
            "funnel_confidence": self.funnel.confidence,
            "primary_topic": self.topic.primary_topic,
            "overall_confidence": self.overall_confidence,
            "conversion_score": self.conversion_score,
            "classification_method": self.classification_method,
        }


# =============================================================================
# REGEX PATTERN DEFINITIONS
# =============================================================================

class ClassificationPatterns:
    """Comprehensive regex patterns for keyword classification (DE + EN)."""

    INTENT_PATTERNS: Dict[IntentType, Dict] = {
        IntentType.TRANSACTIONAL: {
            "patterns": [
                r"\b(kaufen|bestellen|buchen|mieten|abonnieren|ordern)\b",
                r"\b(preis|kosten|günstig|billig|rabatt|angebot|sale|deal)\b",
                r"\b(online\s*(shop|store|kaufen|bestellen))\b",
                r"\b(versandkostenfrei|gratis\s*versand|lieferung)\b",
                r"\b(gutschein|coupon|code|aktion|sonderangebot)\b",
                r"\b(sofort\s*(kaufen|lieferbar|verfügbar))\b",
                r"\b(buy|purchase|order|book|rent|subscribe|get)\b",
                r"\b(price|cost|cheap|affordable|discount|deal|offer|sale)\b",
                r"\b(free\s*shipping|delivery|coupon|promo\s*code)\b",
                r"\b(shop|store|checkout|cart|basket)\b",
                r"\b(add\s*to\s*cart|in\s*den\s*warenkorb)\b",
                r"\b(jetzt\s*(kaufen|bestellen|sichern))\b",
            ],
            "weight": 1.0,
            "conversion_potential": ConversionPotential.HIGH,
            "funnel_stage": FunnelStage.BOFU,
        },
        IntentType.COMMERCIAL: {
            "patterns": [
                r"\b(test|vergleich|bewertung|erfahrung|erfahrungen|rezension)\b",
                r"\b(beste|bester|bestes|top\s*\d+|ranking)\b",
                r"\b(vs\.?|versus|oder|im\s*vergleich|unterschied)\b",
                r"\b(alternative|alternativen|ähnlich|konkurrenz)\b",
                r"\b(empfehlung|empfehlungen|ratgeber|berater)\b",
                r"\b(lohnt\s*sich|wert|sinnvoll)\b",
                r"\b(vor[\-\s]?(und\s*)?nachteile|pro\s*(und|&)\s*contra)\b",
                r"\b(review|reviews|comparison|compare|rating|rated)\b",
                r"\b(best|top\s*\d+|versus|vs\.?)\b",
                r"\b(alternative|similar|like|competitor)\b",
                r"\b(recommendation|guide|advisor)\b",
                r"\b(worth\s*it|pros?\s*(and|&)\s*cons?)\b",
                r"welche[rs]?\s+\w+\s+(ist|sind|für)",
                r"\b(für|for)\s+(anfänger|beginners?|profis?|experts?)\b",
                r"\b(geschenk|geschenke|geschenkidee|geschenkideen|geschenkset)\b",
                r"\b(für\s+(männer|frauen|kinder|freundin|freund|mama|papa|oma|opa))\b",
                r"\b(personalisiert|personalisierte|individuell|individuelle|gravur)\b",
                r"\b(gift|gifts|gift\s*idea|gift\s*set)\b",
                r"\b(for\s+(men|women|kids|her|him|mom|dad))\b",
                r"\b(personalized|personalised|customized|custom|engraved)\b",
            ],
            "weight": 0.85,
            "conversion_potential": ConversionPotential.MEDIUM_HIGH,
            "funnel_stage": FunnelStage.MOFU,
        },
        IntentType.INFORMATIONAL: {
            "patterns": [
                r"\b(was\s+ist|wie\s+(funktioniert|geht|macht\s+man))\b",
                r"\b(warum|wieso|weshalb|wozu|wofür)\b",
                r"\b(wann|wo|wer|welche[rs]?)\b",
                r"\b(definition|bedeutung|erklärung|erklärt)\b",
                r"\b(anleitung|tutorial|guide|tipps?|tricks?)\b",
                r"\b(lernen|verstehen|wissen|info|information)\b",
                r"\b(beispiel|beispiele|vorlage|template)\b",
                r"\b(schritt[\-\s]für[\-\s]schritt|step[\-\s]by[\-\s]step)\b",
                r"\b(what\s+is|how\s+(to|does|do|can|should))\b",
                r"\b(why|when|where|who|which)\b",
                r"\b(definition|meaning|explained|explain)\b",
                r"\b(tutorial|guide|tips?|tricks?|ideas?)\b",
                r"\b(learn|understand|know|info|information)\b",
                r"\?$",
                r"^(kann|können|sollte|darf|muss|ist\s+es)",
                r"^(can|could|should|is\s+it|does|do)\b",
            ],
            "weight": 0.7,
            "conversion_potential": ConversionPotential.LOW,
            "funnel_stage": FunnelStage.TOFU,
        },
        IntentType.NAVIGATIONAL: {
            "patterns": [
                r"\b(login|anmelden|einloggen|registrieren|sign\s*(in|up))\b",
                r"\b(kontakt|impressum|agb|datenschutz|faq)\b",
                r"\b(kundendienst|kundenservice|support|hilfe|help)\b",
                r"\b(homepage|startseite|website|webseite|seite)\b",
                r"\b(app|download|herunterladen)\b",
                r"\b(official|offiziell|offizielle)\b",
                r"\.(com|de|net|org|io)\b",
                r"\b(instagram|facebook|twitter|youtube|tiktok|linkedin)\s+\w+",
            ],
            "weight": 0.5,
            "conversion_potential": ConversionPotential.MEDIUM,
            "funnel_stage": FunnelStage.MOFU,
        },
        IntentType.LOCAL: {
            "patterns": [
                r"\b(in\s+der\s+nähe|in\s+meiner\s+nähe|um\s+die\s+ecke)\b",
                r"\b(bei\s+mir|vor\s+ort|lokal|regional)\b",
                r"\b(filiale|standort|geschäft|laden|store)\b",
                r"\b(öffnungszeiten|geöffnet|offen)\b",
                r"\b(adresse|anfahrt|route|weg)\b",
                r"\b(near\s+me|nearby|close\s+to|around)\b",
                r"\b(local|location|store|branch|office)\b",
                r"\b(opening\s*hours|open|hours)\b",
                r"\b(address|directions|route)\b",
                r"\b\d{5}\b",
                r"\b(berlin|münchen|munich|hamburg|köln|cologne|frankfurt|düsseldorf|stuttgart|leipzig|dortmund|essen|bremen|dresden|hannover|nürnberg)\b",
            ],
            "weight": 0.9,
            "conversion_potential": ConversionPotential.HIGH,
            "funnel_stage": FunnelStage.BOFU,
        },
    }

    MODIFIER_PATTERNS: Dict[str, Dict] = {
        "year": {
            "patterns": [r"\b(20[2-3]\d)\b", r"\b(dieses\s+jahr|this\s+year|aktuell|current|neu|new)\b"],
            "boost": 0.1,
        },
        "location": {
            "patterns": [
                r"\b(deutschland|germany|österreich|austria|schweiz|switzerland)\b",
                r"\b(online|offline|vor\s+ort|lokal)\b",
            ],
            "boost": 0.05,
        },
        "price": {
            "patterns": [
                r"\b(€|\$|euro|dollar|preis|price|kosten|cost)\b",
                r"\b(günstig|cheap|teuer|expensive|billig|affordable)\b",
                r"\b(gratis|kostenlos|free|umsonst)\b",
            ],
            "boost": 0.15,
        },
        "comparison": {
            "patterns": [
                r"\b(vs\.?|versus|oder|or|im\s+vergleich|compared?\s+to)\b",
                r"\b(unterschied|difference|besser|better|schlechter|worse)\b",
            ],
            "boost": 0.1,
        },
        "question": {
            "patterns": [
                r"\?$",
                r"^(was|wie|warum|wann|wo|wer|welche|kann|sollte|ist)",
                r"^(what|how|why|when|where|who|which|can|should|is|does|do)",
            ],
            "boost": 0.05,
        },
        "best_of": {
            "patterns": [
                r"\b(beste|bester|bestes|best|top\s*\d+)\b",
                r"\b(empfohlen|recommended|favorit|favorite)\b",
            ],
            "boost": 0.1,
        },
        "how_to": {
            "patterns": [
                r"\b(anleitung|tutorial|guide|how[\-\s]to)\b",
                r"\b(schritt[\-\s]für[\-\s]schritt|step[\-\s]by[\-\s]step)\b",
                r"\b(lernen|learn|anfänger|beginner)\b",
            ],
            "boost": 0.05,
        },
        "negative": {
            "patterns": [
                r"\b(ohne|without|nicht|not|kein|no|never|niemals)\b",
                r"\b(problem|fehler|error|issue|bug)\b",
            ],
            "boost": -0.05,
        },
    }

    TOPIC_PATTERNS: Dict[str, List[str]] = {
        "ecommerce": [
            r"\b(shop|store|kaufen|bestellen|warenkorb|cart)\b",
            r"\b(produkt|product|artikel|item|ware)\b",
            r"\b(versand|shipping|lieferung|delivery|retoure|return)\b",
        ],
        "fashion": [
            r"\b(mode|fashion|kleidung|clothing|outfit|style)\b",
            r"\b(schuhe|shoes|tasche|bag|schmuck|jewelry|jewellery)\b",
            r"\b(ring|kette|necklace|armband|bracelet|ohrringe|earrings)\b",
            r"\b(kleid|dress|hose|pants|hemd|shirt|jacke|jacket)\b",
        ],
        "technology": [
            r"\b(software|hardware|app|digital|tech|technologie)\b",
            r"\b(computer|laptop|smartphone|tablet|handy|phone)\b",
            r"\b(programmieren|coding|developer|entwickler)\b",
        ],
        "health": [
            r"\b(gesundheit|health|fitness|wellness|sport)\b",
            r"\b(medizin|medical|arzt|doctor|therapie|therapy)\b",
            r"\b(ernährung|nutrition|diät|diet|vitamin|supplement)\b",
        ],
        "finance": [
            r"\b(geld|money|finanzen|finance|bank|kredit|credit)\b",
            r"\b(investieren|invest|aktien|stocks|fonds|fund)\b",
            r"\b(versicherung|insurance|steuer|tax)\b",
        ],
        "travel": [
            r"\b(reise|travel|urlaub|vacation|hotel|flug|flight)\b",
            r"\b(buchen|book|reservieren|reserve)\b",
            r"\b(strand|beach|berg|mountain|see|lake|meer|sea)\b",
        ],
        "food": [
            r"\b(essen|food|kochen|cooking|rezept|recipe)\b",
            r"\b(restaurant|café|lieferservice|delivery)\b",
            r"\b(vegan|vegetarisch|bio|organic)\b",
        ],
        "education": [
            r"\b(lernen|learn|kurs|course|training|schulung)\b",
            r"\b(studium|study|universität|university|schule|school)\b",
            r"\b(zertifikat|certificate|abschluss|degree)\b",
        ],
        "services": [
            r"\b(dienstleistung|service|beratung|consulting)\b",
            r"\b(agentur|agency|firma|company|unternehmen)\b",
            r"\b(anbieter|provider|experte|expert)\b",
        ],
        "seo": [
            r"\b(seo|search\s*engine|suchmaschine)\b",
            r"\b(keyword|backlink|ranking|serp|google)\b",
            r"\b(optimierung|optimization|traffic|conversion)\b",
            r"\b(content|marketing|online\s*marketing|digital\s*marketing)\b",
        ],
    }

    _compiled_cache: Optional[Dict] = None

    @classmethod
    def compile_patterns(cls) -> Dict:
        if cls._compiled_cache:
            return cls._compiled_cache

        compiled: Dict[str, Any] = {"intent": {}, "modifier": {}, "topic": {}}

        for intent_type, config in cls.INTENT_PATTERNS.items():
            compiled["intent"][intent_type] = {
                "patterns": [re.compile(p, re.IGNORECASE) for p in config["patterns"]],
                "weight": config["weight"],
                "conversion_potential": config["conversion_potential"],
                "funnel_stage": config["funnel_stage"],
            }

        for mod_name, config in cls.MODIFIER_PATTERNS.items():
            compiled["modifier"][mod_name] = {
                "patterns": [re.compile(p, re.IGNORECASE) for p in config["patterns"]],
                "boost": config["boost"],
            }

        for topic_name, patterns in cls.TOPIC_PATTERNS.items():
            compiled["topic"][topic_name] = [re.compile(p, re.IGNORECASE) for p in patterns]

        cls._compiled_cache = compiled
        return compiled


# =============================================================================
# BRAND CLASSIFIER
# =============================================================================

class BrandClassifier:
    """Brand and competitor keyword classifier."""

    CHAR_SUBSTITUTIONS = {
        "i": ["e", "y", "1", "l"],
        "e": ["i", "a", "3"],
        "a": ["e", "o", "u"],
        "o": ["u", "0", "i"],
        "u": ["o", "ue", "ou"],
        "c": ["k", "s"],
        "k": ["c", "ck"],
        "ei": ["ey", "ay", "ai", "ie"],
        "ie": ["y", "ee", "ei"],
    }

    def __init__(
        self,
        brand_name: str,
        brand_variations: Optional[List[str]] = None,
        product_keywords: Optional[List[str]] = None,
        competitors: Optional[List[Dict[str, Any]]] = None,
        generate_misspellings: bool = True,
    ):
        self.brand_name = brand_name.lower() if brand_name else ""
        self.brand_variations = self._generate_variations(
            brand_name, brand_variations, generate_misspellings
        )
        self.product_keywords = set(
            kw.lower().strip() for kw in (product_keywords or []) if kw
        )
        self.competitors = self._setup_competitors(competitors or [], generate_misspellings)
        self._brand_pattern = self._create_brand_pattern(self.brand_variations)
        self._competitor_patterns = {
            name: self._create_brand_pattern(vars_)
            for name, vars_ in self.competitors.items()
        }

    def _generate_variations(
        self, brand_name: str, additional: Optional[List[str]] = None, generate_misspellings: bool = True
    ) -> Set[str]:
        if not brand_name:
            return set()
        variations: Set[str] = set()
        base = brand_name.lower().strip()
        variations.add(base)
        variations.add(base.replace(" ", ""))
        variations.add(base.replace(" ", "-"))
        variations.add(base.replace("-", ""))
        if generate_misspellings:
            for i in range(len(base)):
                if base[i].isalpha():
                    variations.add(base[:i] + base[i] + base[i:])
            if len(base) > 3:
                for i in range(len(base)):
                    variations.add(base[:i] + base[i + 1:])
            for original, replacements in self.CHAR_SUBSTITUTIONS.items():
                if original in base:
                    for replacement in replacements:
                        variations.add(base.replace(original, replacement, 1))
            for suffix in [".de", ".com", ".at", ".ch"]:
                variations.add(base + suffix)
        if additional:
            for var in additional:
                if var:
                    variations.add(var.lower().strip())
        return variations

    def _setup_competitors(self, competitors: List[Dict], generate_misspellings: bool) -> Dict[str, Set[str]]:
        result: Dict[str, Set[str]] = {}
        for comp in competitors:
            name = comp.get("name", "").lower()
            if name:
                result[name] = self._generate_variations(
                    comp.get("name"), comp.get("variations"), generate_misspellings
                )
        return result

    def _create_brand_pattern(self, variations: Set[str]) -> Optional[re.Pattern]:
        if not variations:
            return None
        escaped = sorted([re.escape(v) for v in variations if v], key=len, reverse=True)
        if not escaped:
            return None
        return re.compile(r"\b(" + "|".join(escaped) + r")\b", re.IGNORECASE)

    def classify(self, keyword: str) -> BrandClassification:
        if not keyword:
            return BrandClassification(type=BrandType.GENERIC, confidence=0.5)
        normalized = keyword.lower().strip()
        if self._brand_pattern and self._brand_pattern.search(normalized):
            matched_product = None
            for product in self.product_keywords:
                if product in normalized:
                    matched_product = product
                    break
            return BrandClassification(
                type=BrandType.BRAND_PRODUCT if matched_product else BrandType.BRAND,
                confidence=0.95 if matched_product else 1.0,
                matched_brand=self.brand_name,
                matched_product=matched_product,
            )
        for comp_name, pattern in self._competitor_patterns.items():
            if pattern and pattern.search(normalized):
                return BrandClassification(
                    type=BrandType.COMPETITOR, confidence=0.9, matched_brand=comp_name
                )
        for product in self.product_keywords:
            if product in normalized:
                return BrandClassification(
                    type=BrandType.GENERIC, confidence=0.85, matched_product=product
                )
        return BrandClassification(type=BrandType.GENERIC, confidence=0.8)


# =============================================================================
# UNIFIED KEYWORD CLASSIFIER (regex-only)
# =============================================================================

class KeywordClassifier:
    """Keyword classifier using regex patterns. No external dependencies."""

    def __init__(
        self,
        brand_config: Optional[Dict] = None,
        custom_patterns: Optional[Dict] = None,
        cache_enabled: bool = True,
        cache_ttl_seconds: int = 3600,
    ):
        self.brand_classifier: Optional[BrandClassifier] = None
        if brand_config and brand_config.get("brand_name"):
            self.brand_classifier = BrandClassifier(
                brand_name=brand_config.get("brand_name", ""),
                brand_variations=brand_config.get("brand_variations"),
                product_keywords=brand_config.get("product_keywords"),
                competitors=brand_config.get("competitors"),
                generate_misspellings=brand_config.get("generate_misspellings", True),
            )
        self.patterns = ClassificationPatterns.compile_patterns()
        if custom_patterns:
            self._merge_custom_patterns(custom_patterns)
        self.cache_enabled = cache_enabled
        self.cache_ttl = timedelta(seconds=cache_ttl_seconds)
        self._cache: Dict[str, Tuple[ClassificationResult, datetime]] = {}
        self._cache_lock = threading.Lock()

    def _merge_custom_patterns(self, custom: Dict) -> None:
        for intent_type_str, patterns in custom.get("intent", {}).items():
            try:
                intent_type = IntentType(intent_type_str)
                if intent_type in self.patterns["intent"]:
                    compiled = [re.compile(p, re.IGNORECASE) for p in patterns]
                    self.patterns["intent"][intent_type]["patterns"].extend(compiled)
            except ValueError:
                logger.warning(f"Unknown intent type: {intent_type_str}")

    def _get_cache_key(self, keyword: str) -> str:
        brand_hash = self.brand_classifier.brand_name if self.brand_classifier else ""
        return hashlib.md5(f"{keyword.lower()}:{brand_hash}".encode()).hexdigest()

    def _get_from_cache(self, keyword: str) -> Optional[ClassificationResult]:
        if not self.cache_enabled:
            return None
        key = self._get_cache_key(keyword)
        with self._cache_lock:
            if key in self._cache:
                result, timestamp = self._cache[key]
                if datetime.now(timezone.utc) - timestamp < self.cache_ttl:
                    return result
                del self._cache[key]
        return None

    def _set_cache(self, keyword: str, result: ClassificationResult) -> None:
        if not self.cache_enabled:
            return
        key = self._get_cache_key(keyword)
        with self._cache_lock:
            self._cache[key] = (result, datetime.now(timezone.utc))
            if len(self._cache) > CACHE_MAX_SIZE:
                sorted_keys = sorted(self._cache.keys(), key=lambda k: self._cache[k][1])
                for old_key in sorted_keys[:CACHE_EVICTION_SIZE]:
                    del self._cache[old_key]

    def _classify_intent(self, keyword: str) -> IntentClassification:
        normalized = keyword.lower().strip()
        best_match = IntentClassification(
            type=IntentType.INFORMATIONAL, confidence=0.3,
            matched_patterns=[], conversion_potential=ConversionPotential.LOW,
        )
        for intent_type, config in self.patterns["intent"].items():
            match_count = 0
            matched_patterns: List[str] = []
            for pattern in config["patterns"]:
                if pattern.search(normalized):
                    match_count += 1
                    matched_patterns.append(pattern.pattern)
            if match_count > 0:
                confidence = min(0.5 + (match_count * 0.15), config["weight"])
                if confidence > best_match.confidence:
                    best_match = IntentClassification(
                        type=intent_type, confidence=confidence,
                        matched_patterns=matched_patterns[:3],
                        conversion_potential=config["conversion_potential"],
                    )
        return best_match

    def _classify_funnel(self, intent_type: IntentType) -> FunnelClassification:
        funnel_map = {
            IntentType.TRANSACTIONAL: (FunnelStage.BOFU, 0.9, "Bottom of Funnel - Ready to convert"),
            IntentType.COMMERCIAL: (FunnelStage.MOFU, 0.85, "Middle of Funnel - Evaluating options"),
            IntentType.LOCAL: (FunnelStage.BOFU, 0.85, "Bottom of Funnel - Local purchase intent"),
            IntentType.NAVIGATIONAL: (FunnelStage.MOFU, 0.7, "Middle of Funnel - Brand aware"),
            IntentType.INFORMATIONAL: (FunnelStage.TOFU, 0.8, "Top of Funnel - Research phase"),
        }
        stage, confidence, description = funnel_map.get(
            intent_type, (FunnelStage.TOFU, 0.5, "Unknown funnel stage")
        )
        return FunnelClassification(stage=stage, confidence=confidence, description=description)

    def _classify_modifiers(self, keyword: str) -> ModifierClassification:
        normalized = keyword.lower().strip()
        result = ModifierClassification()
        modifier_mapping = {
            "year": "has_year", "location": "has_location", "price": "has_price",
            "comparison": "has_comparison", "question": "has_question",
            "best_of": "has_best_of", "how_to": "has_how_to", "negative": "has_negative",
        }
        for mod_name, config in self.patterns["modifier"].items():
            for pattern in config["patterns"]:
                if pattern.search(normalized):
                    attr_name = modifier_mapping.get(mod_name)
                    if attr_name:
                        setattr(result, attr_name, True)
                        result.detected_modifiers.append(mod_name)
                        result.confidence_boost += config["boost"]
                    break
        return result

    def _classify_topic(self, keyword: str) -> TopicClassification:
        normalized = keyword.lower().strip()
        matches: List[Tuple[str, float]] = []
        for topic_name, patterns in self.patterns["topic"].items():
            match_count = sum(1 for p in patterns if p.search(normalized))
            if match_count > 0:
                matches.append((topic_name, match_count / len(patterns)))
        matches.sort(key=lambda x: x[1], reverse=True)
        if matches:
            return TopicClassification(
                primary_topic=matches[0][0],
                secondary_topics=[m[0] for m in matches[1:4]],
                confidence=matches[0][1],
            )
        return TopicClassification(primary_topic="general", secondary_topics=[], confidence=0.3)

    def _calculate_overall_confidence(
        self, brand: BrandClassification, intent: IntentClassification,
        funnel: FunnelClassification, topic: TopicClassification,
        modifiers: ModifierClassification,
    ) -> float:
        confidence = (
            brand.confidence * 0.25
            + intent.confidence * 0.35
            + funnel.confidence * 0.15
            + topic.confidence * 0.15
        )
        confidence += modifiers.confidence_boost
        return max(0.0, min(1.0, confidence))

    def _calculate_conversion_score(
        self, brand: BrandClassification, intent: IntentClassification,
        modifiers: ModifierClassification,
    ) -> int:
        base_scores = {
            ConversionPotential.HIGH: 80, ConversionPotential.MEDIUM_HIGH: 65,
            ConversionPotential.MEDIUM: 50, ConversionPotential.LOW: 25,
        }
        score = base_scores.get(intent.conversion_potential, 40)
        if brand.type == BrandType.BRAND:
            score += 15
        elif brand.type == BrandType.BRAND_PRODUCT:
            score += 20
        elif brand.type == BrandType.COMPETITOR:
            score += 5
        if modifiers.has_price:
            score += 5
        if modifiers.has_best_of:
            score += 5
        if modifiers.has_year:
            score += 3
        if modifiers.has_negative:
            score -= 10
        return max(0, min(100, score))

    def classify(self, keyword: str) -> ClassificationResult:
        """Classify a single keyword. Returns ClassificationResult."""
        if not keyword or not isinstance(keyword, str):
            raise ValueError("Invalid keyword provided")
        keyword = keyword.strip()
        if not keyword:
            raise ValueError("Invalid keyword provided")
        if len(keyword) > MAX_KEYWORD_LENGTH:
            raise ValueError(f"Keyword exceeds maximum length of {MAX_KEYWORD_LENGTH} characters")

        cached = self._get_from_cache(keyword)
        if cached:
            return cached

        brand_result = (
            self.brand_classifier.classify(keyword)
            if self.brand_classifier
            else BrandClassification(type=BrandType.GENERIC, confidence=0.5)
        )
        intent_result = self._classify_intent(keyword)
        funnel_result = self._classify_funnel(intent_result.type)
        topic_result = self._classify_topic(keyword)
        modifiers_result = self._classify_modifiers(keyword)
        overall_confidence = self._calculate_overall_confidence(
            brand_result, intent_result, funnel_result, topic_result, modifiers_result
        )
        conversion_score = self._calculate_conversion_score(
            brand_result, intent_result, modifiers_result
        )

        result = ClassificationResult(
            keyword=keyword,
            brand=brand_result,
            intent=intent_result,
            funnel=funnel_result,
            topic=topic_result,
            modifiers=modifiers_result,
            overall_confidence=overall_confidence,
            conversion_score=conversion_score,
            classification_method="regex",
        )
        self._set_cache(keyword, result)
        return result

    def classify_batch(self, keywords: List[str]) -> List[ClassificationResult]:
        """Classify multiple keywords."""
        results: List[ClassificationResult] = []
        for kw in keywords:
            try:
                results.append(self.classify(kw))
            except ValueError:
                continue
        return results

    def clear_cache(self) -> None:
        with self._cache_lock:
            self._cache.clear()


# =============================================================================
# MODULE-LEVEL HELPERS
# =============================================================================

_classifier_instance: Optional[KeywordClassifier] = None
_classifier_lock = threading.Lock()


def get_classifier(brand_config: Optional[Dict] = None) -> KeywordClassifier:
    """Thread-safe singleton factory."""
    global _classifier_instance
    with _classifier_lock:
        if _classifier_instance is None:
            _classifier_instance = KeywordClassifier(brand_config=brand_config)
        return _classifier_instance


def quick_classify(keyword: str, brand_config: Optional[Dict] = None) -> ClassificationResult:
    """One-shot classify without setup."""
    classifier = get_classifier(brand_config)
    return classifier.classify(keyword)


def group_by_intent(results: List[ClassificationResult]) -> Dict[str, List[ClassificationResult]]:
    groups: Dict[str, List[ClassificationResult]] = {}
    for r in results:
        key = r.intent.type.value
        groups.setdefault(key, []).append(r)
    return groups


def group_by_funnel(results: List[ClassificationResult]) -> Dict[str, List[ClassificationResult]]:
    groups: Dict[str, List[ClassificationResult]] = {}
    for r in results:
        key = r.funnel.stage.value
        groups.setdefault(key, []).append(r)
    return groups


def filter_high_conversion(results: List[ClassificationResult], min_score: int = 60) -> List[ClassificationResult]:
    return [r for r in results if r.conversion_score >= min_score]


def sort_by_conversion(results: List[ClassificationResult], descending: bool = True) -> List[ClassificationResult]:
    return sorted(results, key=lambda r: r.conversion_score, reverse=descending)
