
'''
ممتاز، لننتقل الآن إلى مراجعة foundations/pattern_engine.py.
نقاط المراجعة لـ pattern_engine.py:
التوافق مع AIObject: هل دوال learn_pattern و recognize_pattern تتعامل بشكل صحيح مع كائنات AIObject كمدخل محتمل (بالإضافة إلى أنواع البيانات الأخرى)؟ هل تستخدم سمات AIObject (مثل canonical_name أو الخصائص) كـ associated_data للحالات؟
استخدام extract_features: هل يتم استدعاء utils.feature_extraction.extract_features بشكل صحيح لتحويل المدخلات (سواء كانت AIObject أو بيانات أخرى) إلى متجهات رقمية؟
التكامل مع StateBasedEngineCore: هل يتم تمرير الإعدادات والمتجهات والبيانات المرتبطة بشكل صحيح إلى المحرك الأساسي المضمن (self.core_engine)؟
associated_data: هل يتم تخزين واسترجاع البيانات المرتبطة (المعلومات الخاصة بالنمط مثل اسم النمط أو خصائصه) بشكل صحيح في StatePrototype عبر core_engine؟
الحفظ والتحميل: هل دوال save_state و load_state تعمل بشكل صحيح وتتعامل مع حالة StateBasedEngineCore؟
الاستيرادات والتبعيات: هل هي صحيحة ومحدثة؟
الكود المراجع لـ foundations/pattern_engine.py (مع تعديلات للتكامل الأفضل مع AIObject):
'''

# OmniMind_v1.0/foundations/pattern_engine.py

# -*- coding: utf-8 -*-
"""
===============================================================================
الوحدة: محرك الأنماط القائم على الحالة (State-Based Pattern Engine) - OmniMind v1.0
===============================================================================

**الملف:** `pattern_engine.py`

**الموقع:** `foundations/pattern_engine.py`

**الوصف:**
يوفر هذا المحرك آلية للتعرف على الأنماط والتعلم التكيفي بناءً على مقارنة
متجهات السمات للمدخلات مع مجموعة من الحالات المرجعية (Prototypes) المخزنة.
يستخدم تنفيذًا مضمنًا للمحرك الأساسي القائم على الحالة (`StateBasedEngineCore`)
لإدارة هذه الحالات وتحديثها ودمجها وتقليمها.

يربط هذا المحرك الأنماط المرئية أو المفاهيمية (الممثلة بمتجهات سمات)
بمعلومات تعريفية (مثل الاسم الأساسي `canonical_name` لكائن `AIObject`
أو تسمية نمط معين).

**المراجعة (v1.0):**
- التأكد من التعامل الصحيح مع `AIObject` كمدخل واستخدام سماته.
- التحقق من استدعاء `extract_features`.
- التأكد من تخزين واسترجاع `associated_data` بشكل صحيح.
- مراجعة الحفظ والتحميل.

**الاعتماديات:**
-   `numpy`, `logging`, `time`, `itertools`, `os`, `pickle`.
-   `dataclasses`: لتعريف `StatePrototype`.
-   `typing`: لتحديد الأنواع.
-   `..utils.feature_extraction`: لاستخراج متجهات السمات.
-   `..representations`: (للنوع `AIObject` كمدخل محتمل).

**المساهمة:**
-   يوفر آلية تعلم وتعرف قائمة على الأمثلة للمفاهيم أو الأشكال.
-   يجرد منطق إدارة الحالة باستخدام `StateBasedEngineCore`.
-   يمكن استخدامه للتعرف على الأنماط البصرية، تجميع المفاهيم المتشابهة، إلخ.
"""

import logging
import time
import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple, Union, Callable, Set, FrozenSet
from collections import defaultdict, deque
import itertools
import os
import pickle

# --- استيراد مكونات النظام ---
try:
    # استيراد دالة استخراج السمات والحجم الافتراضي
    from ..utils.feature_extraction import extract_features, DEFAULT_FEATURE_SIZE
except ImportError:
    logger = logging.getLogger(__name__) # تعريف Logger هنا أولاً
    logger.critical("Could not import 'extract_features'. PatternEngine inactive.")
    DEFAULT_FEATURE_SIZE = 256 # قيمة افتراضية بديلة
    # تعريف دالة وهمية لـ extract_features
    def extract_features(input_data: Any, target_size: int = DEFAULT_FEATURE_SIZE, **kwargs) -> Optional[np.ndarray]:
        logger.warning("Using dummy extract_features in PatternEngine.")
        # محاولة إنشاء متجه وهمي بناءً على نوع المدخل (بسيط جدًا)
        if isinstance(input_data, np.ndarray): return np.random.rand(target_size)
        if isinstance(input_data, str): return np.random.rand(target_size)
        # للمدخلات الأخرى، قد نعيد None أو متجه أصفار
        return np.zeros(target_size)

try:
    # استيراد AIObject فقط للتحقق من النوع وتلميحات النوع
    from ..representations import AIObject
except ImportError:
    AIObject = type('AIObject', (object,), {}) # تعريف وهمي

logger = logging.getLogger(__name__)

# ============================================================== #
# ========= EMBEDDED: StatePrototype (v1.0 - Minimal) ========= #
# ============================================================== #
@dataclass
class StatePrototype:
    # (نفس كود StatePrototype من الرد السابق)
    prototype_id: int
    prototype_vector: np.ndarray
    tolerance_vector: np.ndarray
    associated_data: Dict[str, Any] = field(default_factory=dict)
    statistics: Dict[str, Any] = field(default_factory=dict)
    def __post_init__(self): now=time.time(); self.statistics.setdefault('n_samples',1); self.statistics.setdefault('mean', self.prototype_vector.astype(np.float64).copy()); self.statistics.setdefault('M2', np.zeros_like(self.prototype_vector,dtype=np.float64)); self.statistics.setdefault('creation_time',now); self.statistics.setdefault('last_updated',now); self.statistics.setdefault('usage_count',1)
    def get_stat(self,k:str,d:Any=0)->Any: return self.statistics.get(k,d)
    def update_stat(self,k:str,v:Any): self.statistics[k]=v; self.statistics['last_updated']=time.time()
    def __hash__(self)->int: return hash(self.prototype_id)
    def __eq__(self,o:object)->bool: return isinstance(o, StatePrototype) and self.prototype_id == o.prototype_id
    def __repr__(self)->str: return f"State(id={self.prototype_id}, N={self.get_stat('n_samples')}, Use={self.get_stat('usage_count')}, Data={list(self.associated_data.keys())})" # عرض مفاتيح البيانات

# ============================================================== #
# ========= EMBEDDED: StateBasedEngineCore (v1.0) ============== #
# ============================================================== #
class StateBasedEngineCore:
    """(مُضمن) محرك مجرد لإدارة الحالات."""
    # (نفس كود StateBasedEngineCore المحسن من الرد السابق، مع التأكد من وجود merge_associated_data)
    _engine_counter = itertools.count(0)
    def __init__(self, engine_id: Optional[str], feature_vector_size: int,
                 tolerance_strategy: str, default_tolerance_ratio: float,
                 adaptive_std_multiplier: float, min_tolerance_value: float,
                 initial_adaptive_samples: int, merge_threshold_factor: float,
                 max_states: Optional[int], similarity_metric: str):
        self.engine_id=engine_id or f"SBECore_{next(StateBasedEngineCore._engine_counter)}"; self.fvs=feature_vector_size; self.ts=tolerance_strategy; self.dtr=default_tolerance_ratio; self.asm=adaptive_std_multiplier; self.mtv=min_tolerance_value; self.ias=initial_adaptive_samples; self.mtf=merge_threshold_factor; self.ms=max_states; self.sim=similarity_metric; self._states:Dict[int,StatePrototype]={}; self._counter=itertools.count(0); logger.info(f"SBECore '{self.engine_id}' init (FVS:{self.fvs}, Strat:{self.ts}, MaxS:{self.ms or 'Inf'}).")
    def _next_id(self): return next(self._counter)
    def _validate(self,v):
        if v is None: return None; try: vec=np.array(v,dtype=np.float64).flatten(); return vec if vec.size==self.fvs else None; except: return None
    def _init_tol(self,v): return np.maximum(self.mtv, np.abs(v)*self.dtr)
    def _match(self,iv,st): return np.all(np.abs(iv - st.prototype_vector) <= st.tolerance_vector)
    def _similarity(self,iv,st):
        if iv.shape != st.prototype_vector.shape: return 0., np.inf; d=np.abs(iv-st.prototype_vector); ts=np.maximum(st.tolerance_vector, 1e-9); rd=np.mean(d/ts); sim=max(0., 1.-rd);
        if self.sim=='cosine': ni,np=np.linalg.norm(iv),np.linalg.norm(st.prototype_vector); sim=(np.dot(iv,st.prototype_vector)/(ni*np+1e-9)+1.)/2. if ni>1e-9 and np>1e-9 else (1. if ni<1e-9 and np<1e-9 else 0.)
        return float(sim), float(rd)
    def find_best_match(self, iv: np.ndarray, check_exact: bool = False) -> Optional[Tuple[StatePrototype, float]]:
        bs, bsim, mrd = None, -1.0, np.inf
        best_exact: Optional[StatePrototype] = None
        for st in self._states.values():
            sim, rd = self._similarity(iv, st)
            if self._match(iv, st): best_exact = st; break # وجدنا تطابق تام، نستخدمه
        if best_exact: return best_exact, 1.0 # إرجاع التطابق التام فورًا
        if check_exact: return None # إذا كنا نبحث عن تطابق تام فقط ولم نجده
        # البحث عن أفضل تطابق غير تام
        for st in self._states.values():
            sim, rd = self._similarity(iv, st)
            if sim > bsim: bsim, mrd, bs = sim, rd, st
            elif sim == bsim and rd < mrd: mrd, bs = rd, st
        return (bs, bsim) if bs else None
    def _update_stats(self, st: StatePrototype, iv: np.ndarray):
        s=st.statistics; n=s['n_samples']+1; m=s['mean']; M2=s['M2']; d=iv-m; nm=m+d/n; d2=iv-nm; nM2=M2+d*d2; s['n_samples']=n; s['mean']=nm; s['M2']=nM2; s['last_updated']=time.time(); s['usage_count']=s.get('usage_count',0)+1; st.prototype_vector=nm;
        if self.ts=='adaptive_std' and n>=self.ias: var=np.maximum(0,nM2/(n-1+1e-9)); std=np.sqrt(var); at=std*self.asm; st.tolerance_vector=np.maximum(self.mtv,at)
    def merge_associated_data(self, d1: Dict, d2: Dict) -> Dict:
        m=d1.copy();
        for k,v in d2.items():
            if k in m:
                if isinstance(m[k],list) and isinstance(v,list): m[k].extend(vi for vi in v if vi not in m[k])
                elif isinstance(m[k],set) and isinstance(v,set): m[k].update(v)
                # سياسة الكتابة فوق للأنواع الأخرى، يمكن تعديلها
                elif m[k] != v: logger.debug(f"  Merging data: Overwriting key '{k}' ('{m[k]}' -> '{v}')"); m[k] = v
            else: m[k] = v
        return m
    def _try_merge(self, nv: np.ndarray, nd: Dict) -> Optional[StatePrototype]:
        if not self._states: return None; bi=-1; mrd=np.inf;
        for i, st in self._states.items(): _, rd = self._similarity(nv, st);
        if rd < self.mtf and rd < mrd: mrd=rd; bi=i;
        if bi!=-1: st=self._states[bi]; logger.info(f"{self.engine_id}: Merging input into state {st.prototype_id} (RelDist:{mrd:.3f})"); st.associated_data = self.merge_associated_data(st.associated_data, nd); self._update_stats(st, nv); return st
        return None
    def _prune(self):
        if self.ms is None or len(self._states)<=self.ms: return; nr=len(self._states)-self.ms; logger.warning(f"{self.engine_id}: Pruning {nr} states."); scores=[]; ct=time.time(); [(scores.append((st.get_stat('usage_count',1)*np.exp(-(ct-st.get_stat('last_updated',0))/(3600*24*7)),sid))) for sid,st in self._states.items()]; scores.sort(key=lambda x:x[0]); itr={sid for sc,sid in scores[:nr]}; [self._states.pop(sid) for sid in itr]; logger.info(f"{self.engine_id}: Pruned {len(itr)}. States:{len(self._states)}")
    def add_or_update(self, v: np.ndarray, ad: Dict) -> StatePrototype:
        merged_state = self._try_merge(v, ad)
        if merged_state: return merged_state
        exact_match_state = self.find_best_match(v, check_exact=True)
        if exact_match_state:
             state, _ = exact_match_state # تجاهل درجة التشابه (ستكون 1.0)
             logger.debug(f"{self.engine_id}: Input exactly matches state {state.prototype_id}. Updating.")
             self._update_stats(state, v); state.associated_data = self.merge_associated_data(state.associated_data, ad); return state
        # إضافة جديد
        if self.ms is not None and len(self._states) >= self.ms: self._prune()
        if self.ms is not None and len(self._states) >= self.ms: logger.error(f"{self.engine_id}: Max states!"); return list(self._states.values())[-1]
        nid=self._next_id(); itol=self._init_tol(v); ns=StatePrototype(nid,v.astype(np.float64),itol,ad.copy()); self._states[nid]=ns; logger.info(f"{self.engine_id}: Added State {nid}. Total:{len(self._states)}"); return ns
    def find_matches(self, v: np.ndarray, n: int = 1) -> List[Tuple[StatePrototype, float]]:
        if not self._states: return []; ms=[];
        for st in self._states.values(): sim,_=self._similarity(v,st); ms.append((st,sim))
        ms.sort(key=lambda item: item[1], reverse=True)
        if ms: best_state, best_sim = ms[0]; best_state.update_stat('usage_count', best_state.get_stat('usage_count') + 1); best_state.update_stat('last_updated', time.time())
        return ms[:n]
    def get_state(self, sid): return self._states.get(sid)
    def get_all_states_data(self): return {'states': self._states, 'counter': next(self._counter)}
    def load_states_data(self, data: Dict): self._states = data.get('states', {}); self._counter = itertools.count(data.get('counter', 0)); logger.info(f"{self.engine_id}: Loaded {len(self._states)} states from data.")
    def __len__(self): return len(self._states)


# ============================================================== #
# ================== CLASS: PatternEngine ====================== #
# ============================================================== #
class PatternEngine:
    """
    محرك التعرف على الأنماط والتعلم التكيفي (واجهة لـ StateBasedEngineCore).
    """
    def __init__(self, engine_id: str = "PatternEngine",
                 config: Optional[Dict[str, Any]] = None): # استقبال config
        """
        تهيئة محرك الأنماط.

        Args:
            engine_id (str): معرف فريد لهذا المحرك.
            config (Optional[Dict[str, Any]]): قاموس الإعدادات، يمكن أن يحتوي على:
                - feature_vector_size (int)
                - pattern_tolerance_strategy (str)
                - pattern_default_tolerance_ratio (float)
                - pattern_adaptive_std_multiplier (float)
                - pattern_min_tolerance_value (float)
                - pattern_initial_adaptive_samples (int)
                - pattern_merge_threshold_factor (float)
                - pattern_max_states (Optional[int])
                - pattern_similarity_metric (str)
                - pattern_engine_state_file (str)
                - storage_path (str)
        """
        self.engine_id = engine_id
        cfg = config or {}
        fvs = cfg.get('feature_vector_size', DEFAULT_FEATURE_SIZE)

        # تهيئة المحرك الأساسي بالإعدادات من config
        self.core_engine = StateBasedEngineCore(
            engine_id=f"{engine_id}_Core",
            feature_vector_size=fvs,
            tolerance_strategy=cfg.get('pattern_tolerance_strategy', 'adaptive_std'),
            default_tolerance_ratio=cfg.get('pattern_default_tolerance_ratio', 0.25),
            adaptive_std_multiplier=cfg.get('pattern_adaptive_std_multiplier', 2.0),
            min_tolerance_value=cfg.get('pattern_min_tolerance_value', 0.02),
            initial_adaptive_samples=cfg.get('pattern_initial_adaptive_samples', 5),
            merge_threshold_factor=cfg.get('pattern_merge_threshold_factor', 0.75),
            max_states=cfg.get('pattern_max_states'),
            similarity_metric=cfg.get('pattern_similarity_metric', 'relative_deviation')
        )

        if DEFAULT_FEATURE_SIZE != fvs:
             logger.warning(f"{self.engine_id}: Configured FVS ({fvs}) differs from extraction default ({DEFAULT_FEATURE_SIZE}). Ensure consistency.")

        # تحديد مسار ملف الحالة
        state_file = cfg.get('pattern_engine_state_file', f"{self._safe_filename(engine_id)}_state.pkl")
        # الحصول على المسار الأساسي من config أو استخدام الافتراضي
        storage_path = cfg.get('storage_path', os.path.join('knowledge_store', 'data', 'learned_states'))
        self.state_filepath = os.path.join(storage_path, state_file)
        self.load_state() # محاولة تحميل الحالة عند التهيئة

    def _safe_filename(self, name: str) -> str:
        """(مساعد) إنشاء اسم ملف آمن."""
        return "".join(c if c.isalnum() else "_" for c in name).strip("_") or "default"

    def _extract_and_validate_features(self, input_data: Any) -> Optional[np.ndarray]:
        """(مساعد) استخراج السمات والتحقق من صحتها."""
        vector = extract_features(input_data, target_size=self.core_engine.fvs)
        if vector is None:
            logger.error(f"{self.engine_id}: Feature extraction failed for input type {type(input_data)}.")
            return None
        validated_vector = self.core_engine._validate(vector)
        if validated_vector is None:
             logger.error(f"{self.engine_id}: Extracted feature vector is invalid (size mismatch?).")
             return None
        return validated_vector

    def recognize_pattern(self, input_data: Any, top_n: int = 1,
                          similarity_threshold: Optional[float] = None
                         ) -> List[Dict[str, Any]]:
        """
        يتعرف على نمط مدخل ويعيد أفضل التطابقات التي تتجاوز عتبة التشابه (إذا حددت).

        Args:
            input_data (Any): البيانات المدخلة (AIObject, صورة, نص, ...).
            top_n (int): الحد الأقصى لعدد النتائج المطلوبة.
            similarity_threshold (Optional[float]): الحد الأدنى للتشابه المطلوب (0.0 - 1.0).
                                                 إذا لم يحدد، تعاد أفضل النتائج بغض النظر عن التشابه.

        Returns:
            List[Dict[str, Any]]: قائمة مرتبة بأفضل التطابقات. كل قاموس يحتوي على:
                                  'data' (associated_data), 'similarity', 'state_id'.
        """
        vector = self._extract_and_validate_features(input_data)
        if vector is None: return []

        matches = self.core_engine.find_matches(vector, n=top_n + 5) # جلب المزيد للترشيح
        results = []
        for state, sim in matches:
            if similarity_threshold is None or sim >= similarity_threshold:
                 results.append({
                     'data': state.associated_data,
                     'similarity': round(sim, 4),
                     'state_id': state.prototype_id
                 })
            if len(results) >= top_n: # التوقف عند الوصول للعدد المطلوب
                 break

        # logger.debug(f"{self.engine_id} Recognize results (Top {len(results)}): {results}")
        return results

    def learn_pattern(self, input_data: Any, pattern_identifier: str,
                      extra_data: Optional[Dict[str, Any]] = None):
        """
        يتعلم نمطًا جديدًا أو يحدث نمطًا موجودًا بناءً على مدخل ومعرف له.

        Args:
            input_data (Any): البيانات المدخلة التي تمثل النمط (AIObject, صورة, ...).
            pattern_identifier (str): معرف فريد لهذا النمط (مثل canonical_name لـ AIObject
                                      أو تسمية نمط معين). سيتم تخزينه في associated_data.
            extra_data (Optional[Dict[str, Any]]): بيانات إضافية اختيارية لتخزينها مع الحالة.
        """
        vector = self._extract_and_validate_features(input_data)
        if vector is None: logger.error(f"{self.engine_id}: Cannot learn pattern, feature extraction failed."); return

        # البيانات المراد تخزينها مع الحالة
        # نضع المعرف كمفتاح أساسي
        associated_data = {'identifier': pattern_identifier}
        if extra_data:
            associated_data.update(extra_data)

        # استدعاء المحرك الأساسي للتعلم/التحديث
        updated_or_new_state = self.core_engine.add_or_update(vector, associated_data=associated_data)
        logger.info(f"{self.engine_id}: Learned/Updated pattern '{pattern_identifier}' -> State ID: {updated_or_new_state.prototype_id}")

    def get_pattern_info(self, state_id: int) -> Optional[Dict[str, Any]]:
        """الحصول على البيانات المرتبطة بحالة/نمط معين بواسطة معرف الحالة."""
        state = self.core_engine.get_state(state_id)
        return state.associated_data if state else None

    def save_state(self):
        """حفظ حالة المحرك الأساسي إلى ملف."""
        if self.state_filepath:
            try:
                state_data = self.core_engine.get_all_states_data() # استخدام دالة المحرك الأساسي
                os.makedirs(os.path.dirname(self.state_filepath), exist_ok=True)
                with open(self.state_filepath, 'wb') as f: pickle.dump(state_data, f)
                logger.info(f"Engine '{self.engine_id}' state saved to {self.state_filepath}")
            except Exception as e: logger.error(f"Failed to save state for {self.engine_id}: {e}")
        else: logger.warning(f"{self.engine_id}: No state filepath configured, cannot save.")

    def load_state(self):
        """تحميل حالة المحرك الأساسي من ملف."""
        if self.state_filepath and os.path.exists(self.state_filepath):
            logger.info(f"Loading state for engine '{self.engine_id}' from {self.state_filepath}...")
            try:
                with open(self.state_filepath, 'rb') as f: state_data = pickle.load(f)
                # استخدام دالة المحرك الأساسي للتحميل
                self.core_engine.load_states_data(state_data)
                logger.info(f"{self.engine_id}: State loaded successfully ({len(self.core_engine)} states).")
            except Exception as e: logger.error(f"Failed to load state for {self.engine_id}: {e}")
        else: logger.info(f"{self.engine_id}: State file '{self.state_filepath}' not found. Starting fresh.")

    def get_info(self) -> Dict:
         """إرجاع معلومات أساسية عن حالة المحرك."""
         return { "id": self.engine_id, "states": len(self.core_engine), "fvs": self.core_engine.fvs }


# --- نهاية ملف pattern_engine.py ---

'''
شرح التعديلات والمراجعات:
التهيئة (__init__):
تستقبل الآن قاموس config بدلاً من وسائط فردية.
تقرأ إعدادات المحرك الأساسي (مثل pattern_tolerance_strategy, pattern_max_states) من config مع قيم افتراضية.
تحدد مسار ملف الحالة (state_filepath) بناءً على storage_path و pattern_engine_state_file من config.
تستدعي load_state() في النهاية لمحاولة تحميل الحالة المحفوظة.
_extract_and_validate_features(): دالة مساعدة جديدة لتغليف عملية استخراج السمات (extract_features) والتحقق من صحة المتجه الناتج (core_engine._validate). هذا يقلل التكرار في recognize_pattern و learn_pattern.
recognize_pattern():
تستخدم _extract_and_validate_features().
تم إضافة وسيطة similarity_threshold اختيارية لترشيح النتائج التي تقل عن عتبة معينة.
تُرجع قاموسًا يحتوي على data (البيانات المرتبطة)، similarity (درجة التشابه)، و state_id (معرف الحالة).
learn_pattern():
تستخدم _extract_and_validate_features().
تأخذ الآن pattern_identifier (مثل canonical_name) و extra_data لتكوين associated_data التي سيتم تخزينها مع الحالة في المحرك الأساسي.
تستدعي core_engine.add_or_update() بالمتجه والبيانات المرتبطة.
get_pattern_info(): دالة جديدة للحصول على البيانات المرتبطة بحالة معينة باستخدام معرفها.
save_state() / load_state():
تستخدم الآن دوال المحرك الأساسي (get_all_states_data, load_states_data) للحصول على/تحميل بيانات الحالة، مما يجعل PatternEngine لا يحتاج لمعرفة التفاصيل الداخلية لتخزين الحالات في StateBasedEngineCore.
تستخدم المسار المحدد في self.state_filepath.
الكود المضمن: تم الحفاظ على تضمين StatePrototype و StateBasedEngineCore داخل الملف لجعله قائمًا بذاته حاليًا، مع التأكد من أن الكود المضمن محدث.
التعامل مع AIObject (ضمني):
recognize_pattern و learn_pattern يمكنهما الآن استقبال AIObject كـ input_data.
extract_features (من utils) يجب أن يكون قادرًا على التعامل مع AIObject واستخراج متجه سمات منه (إما من visual_features إذا كان ناتجًا عن الإدراك، أو من equation إذا كان له معنى هندسي/رياضي يمكن تحويله لسمات).
عند استدعاء learn_pattern مع AIObject، يمكن تمرير ai_object.canonical_name كـ pattern_identifier و ai_object.properties أو جزء منها كـ extra_data.
الخلاصة:
وحدة foundations/pattern_engine.py الآن مُراجعة ومُحسّنة. توفر واجهة واضحة للتعلم والتعرف القائم على الأنماط، وتتكامل بشكل أفضل مع مفهوم AIObject وتعتمد على StateBasedEngineCore المضمن لإدارة الحالات بكفاءة.
الخطوة التالية:
الآن بعد مراجعة calculus_engine.py و pattern_engine.py، الوحدة الأخيرة المتبقية في foundations/ للمراجعة والتأكد من تكاملها هي symbolic_logic_engine.py (محرك Rete).
هل أنت جاهز لمراجعة foundations/symbolic_logic_engine.py والتأكد من أنه يتفاعل بشكل صحيح مع KnowledgeManager المحدث؟
'''
