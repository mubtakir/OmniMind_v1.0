```python
# -*- coding: utf-8 -*-
"""
===============================================================================
نقطة الدخول الرئيسية لنظام OmniMind v1.0
===============================================================================

**الملف:** `main.py`

**الموقع:** جذر المشروع (`OmniMind_v1.0/`)

**الوصف:**
يعمل هذا الملف كنقطة دخول رئيسية لتشغيل نظام OmniMind v1.0.
يقوم بالمهام التالية:
-   تحليل وسائط سطر الأوامر لتحديد وضع التشغيل والإعدادات الأساسية.
-   تحميل التكوين العام للنظام من ملف `config.yaml`.
-   إعداد وتكوين نظام التسجيل (logging) مركزيًا.
-   تهيئة المحرك المركزي `OmniMindEngine` الذي يقوم بدوره بتهيئة
    وتنسيق جميع الوحدات الفرعية للنظام.
-   توجيه التنفيذ إلى الوضع المطلوب (تفاعلي، رسومي، اختبار).
-   ضمان حفظ حالة النظام عند الخروج.

**التشغيل:**
```bash
python main.py [خيارات]

استخدم python main.py --help لعرض الخيارات المتاحة.
"""

import argparse
import logging
import sys
import time
import os
import yaml # لاستيراد ملف التكوين

# استيراد المكونات الرئيسية
# المحرك المركزي هو نقطة البداية الرئيسية التي ستحمل الباقي
try:
    from core.omnimind_engine import OmniMindEngine
except ImportError as e:
    print(f"خطأ فادح: لا يمكن استيراد OmniMindEngine من core. تأكد من أن المسارات صحيحة وأن الحزمة مثبتة بشكل صحيح. الخطأ: {e}", file=sys.stderr)
    sys.exit(1)

# استيراد الواجهات ووظائف الاختبار
try:
    from user_interfaces.cli_interface import start_interactive_shell
except ImportError:
    # تعريف وهمي إذا لم تكن الواجهة موجودة أو هناك مشكلة
    def start_interactive_shell(*args, **kwargs):
        print("خطأ: الواجهة التفاعلية (cli_interface) غير متاحة.", file=sys.stderr)
        raise NotImplementedError("CLI Interface is missing.")

try:
    # استيراد مشروط لواجهة Tkinter
    import tkinter
    from user_interfaces.desktop_interface import NLPApp, TKINTER_AVAILABLE
except ImportError:
    TKINTER_AVAILABLE = False
    NLPApp = None # تعريف وهمي
    print("تحذير: Tkinter غير متاح، الواجهة الرسومية (--gui) لن تعمل.", file=sys.stderr)

# استيراد وظيفة تشغيل الاختبارات (سنفترض أنها موجودة الآن)
try:
    from tests.run_tests import run_all_tests # افتراض وجود ملف run_tests.py في tests/
except ImportError:
    def run_all_tests() -> bool:
        print("خطأ: وظيفة تشغيل الاختبارات غير متاحة (tests/run_tests.py).", file=sys.stderr)
        print("يمكن تشغيل الاختبارات يدويًا باستخدام: python -m unittest discover tests")
        return False # اعتبارها فشلًا

# إعداد التسجيل (يمكن تحسينه بنقله إلى utils.logger_config)
# سيتم إعادة تكوينه بعد قراءة ملف config.yaml
logging.basicConfig(level=logging.WARNING, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("OmniMind_Main")

# تحليل وسائط سطر الأوامر
def parse_arguments():
    """تحليل وفهم وسائط سطر الأوامر المدخلة."""
    parser = argparse.ArgumentParser(
        description="OmniMind v1.0 - Cognitive Architecture based on AI_OOP",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter # يعرض القيم الافتراضية
    )

    # وضع التشغيل
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--interactive", "-i", action="store_const", dest="mode", const="interactive",
        help="Run the interactive command-line shell (default)."
    )
    mode_group.add_argument(
        "--gui", "-g", action="store_const", dest="mode", const="gui",
        help="Run the graphical user interface (requires Tkinter)."
    )
    mode_group.add_argument(
        "--test", "-t", action="store_const", dest="mode", const="test",
        help="Run the unit and integration tests."
    )
    # يمكن إضافة وضع --example لاحقًا
    parser.set_defaults(mode='interactive')

    # ملف التكوين
    parser.add_argument(
        "--config", "-c", type=str, default="config.yaml",
        help="Path to the YAML configuration file."
    )

    # تجاوزات التكوين (أمثلة)
    parser.add_argument(
        "--analyzer", "-a", type=str, default=None,
        choices=['dummy', 'nltk', 'camel', 'bert'], # تحديد الخيارات المتاحة
        help="Override the NLP analyzer specified in the config file."
    )
    parser.add_argument(
        "--log", type=str, default=None,
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help="Override the logging level specified in the config file."
    )
    # يمكن إضافة تجاوزات أخرى هنا (مثل --device لـ BERT)

    return parser.parse_args()

# تحميل التكوين
def load_config(config_path: str) -> Dict[str, Any]:
    """تحميل التكوين من ملف YAML."""
    config: Dict[str, Any] = {}
    if not os.path.exists(config_path):
        logger.warning(f"Configuration file not found at: {config_path}. Using default settings.")
        # يمكن تحديد قيم افتراضية أساسية هنا
        config = {
            'logging': {'level': 'INFO'},
            'nlp': {'default_analyzer': 'dummy'} # افتراضي آمن
        }
    else:
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            logger.info(f"Configuration loaded successfully from: {config_path}")
        except ImportError:
            logger.error("PyYAML library not installed. Cannot load YAML config. Install with: pip install pyyaml")
            # استخدام إعدادات افتراضية بديلة
            config = {'logging': {'level': 'INFO'}, 'nlp': {'default_analyzer': 'dummy'}}
        except yaml.YAMLError as e:
            logger.error(f"Error parsing configuration file {config_path}: {e}", exc_info=True)
            print(f"خطأ: فشل تحليل ملف التكوين {config_path}. تأكد من صحة صيغة YAML.", file=sys.stderr)
            sys.exit(1) # الخروج لأن التكوين ضروري
        except Exception as e:
            logger.error(f"Unexpected error loading configuration: {e}", exc_info=True)
            sys.exit(1)

    return config if config else {} # إرجاع قاموس فارغ إذا فشل التحميل بشكل غريب

# إعداد التسجيل النهائي
def setup_final_logging(config: Dict[str, Any], cli_log_override: Optional[str]):
    """إعادة تكوين التسجيل بناءً على التكوين والتجاوزات."""
    log_config = config.get('logging', {})
    level_str = cli_log_override or log_config.get('level', 'INFO').upper()
    level = getattr(logging, level_str, logging.INFO)

    log_format = log_config.get('format', '%(asctime)s [%(levelname)-8s] %(name)-25s: %(message)s')
    date_format = log_config.get('date_format', '%Y-%m-%d %H:%M:%S')
    log_file = log_config.get('file')

    handlers = [logging.StreamHandler(sys.stdout)]
    if log_file:
        try:
            # التأكد من وجود المجلد
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            handlers.append(logging.FileHandler(log_file, encoding='utf-8'))
        except Exception as e:
            logger.error(f"Could not create log file handler for {log_file}: {e}")

    # إعادة تكوين الـ logger الجذر
    # remove existing handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    # add new handlers
    logging.basicConfig(level=level, format=log_format, datefmt=date_format, handlers=handlers)

    # تعيين مستويات مختلفة للمكتبات المزعجة
    logging.getLogger("transformers").setLevel(log_config.get('transformers_level', 'WARNING').upper())
    logging.getLogger("nltk").setLevel(log_config.get('nltk_level', 'WARNING').upper())
    logging.getLogger("matplotlib").setLevel(log_config.get('matplotlib_level', 'WARNING').upper())

    logger.info(f"Logging configured. Level: {level_str}. File: {log_file or 'None'}.")

# نقطة الدخول الرئيسية
def main():
    """الوظيفة الرئيسية لتحليل الوسائط، تهيئة المحرك، وتوجيه التنفيذ."""
    args = parse_arguments()

    # 1. تحميل التكوين
    config = load_config(args.config)

    # 2. إعداد التسجيل النهائي
    setup_final_logging(config, args.log)

    logger.info(f"OmniMind v1.0 starting up...")
    logger.info(f"Selected run mode: {args.mode}")
    logger.debug(f"Command line arguments: {args}")
    logger.debug(f"Loaded configuration: {config}")

    # 3. تهيئة المحرك المركزي (هو من يقوم بتهيئة كل شيء آخر)
    engine: Optional[OmniMindEngine] = None
    initialization_ok = False
    try:
        logger.info("Initializing OmniMind Engine...")
        start_init_time = time.time()
        # تمرير التكوين والوسائط للمحرك للتعامل مع التجاوزات الداخلية
        engine = OmniMindEngine(config=config, cli_args=args)
        end_init_time = time.time()
        # التأكد من أن المحرك تم تهيئته بالفعل وأن الوحدات المطلوبة متاحة
        # (يمكن إضافة دالة check_readiness() لـ OmniMindEngine)
        if engine: # and engine.check_readiness(required_for_mode=args.mode):
            initialization_ok = True
            logger.info(f"OmniMind Engine initialized successfully ({end_init_time - start_init_time:.2f}s).")
        else:
            logger.critical("OmniMind Engine object could not be created.")

    except Exception as e:
        logger.critical(f"Fatal error during OmniMind Engine initialization: {e}", exc_info=True)
        print(f"\n!!! خطأ فادح أثناء تهيئة المحرك الرئيسي. راجع السجلات.\n", file=sys.stderr)
        sys.exit(1)

    if not initialization_ok:
        logger.critical("Engine initialization failed or required modules are missing. Exiting.")
        sys.exit(1)

    # --- 4. تنفيذ الوضع المحدد ---
    final_status_ok = True
    exit_code = 0
    try:
        if args.mode == "interactive":
            logger.info("Starting interactive shell...")
            # الواجهة التفاعلية قد تحتاج للمحرك بأكمله
            start_interactive_shell(engine)
        elif args.mode == "gui":
            if not TKINTER_AVAILABLE or not NLPApp:
                logger.error("Cannot start GUI mode: Tkinter is not available or NLPApp failed to import.")
                final_status_ok = False; exit_code = 1
            else:
                logger.info("Starting graphical user interface...")
                # الواجهة الرسومية تحتاج للمكونات، يمكن للمحرك توفيرها
                analyzer = engine.get_module('language').analyzer # مثال للوصول للمحلل
                kb = engine.get_module('knowledge_manager')
                mapper = engine.get_module('semantic_mapper') # افتراض اسم الوحدة
                coref = engine.get_module('coreference_resolver') # افتراض اسم الوحدة
                use_rete = isinstance(engine.get_module('symbolic_logic_engine'), ReteNetwork)

                if not all([analyzer, kb, mapper, coref]):
                    logger.error("One or more required components for GUI are missing in the engine.")
                    final_status_ok = False; exit_code = 1
                else:
                    app = NLPApp(kb, analyzer, mapper, coref, use_rete=use_rete)
                    app.run() # بدء حلقة الواجهة
        elif args.mode == "test":
            logger.info("Running tests...")
            final_status_ok = run_all_tests()
            exit_code = 0 if final_status_ok else 1
        # elif args.mode == "example":
        #     logger.info("Running main example...")
        #     # final_status_ok = run_main_example(engine) # تمرير المحرك
        #     logger.warning("Example mode not fully implemented yet.")

    except NotImplementedError as nie:
        logger.error(f"Execution failed: Feature not implemented: {nie}", exc_info=True)
        final_status_ok = False; exit_code = 1
    except Exception as main_exec_error:
        logger.critical(f"Fatal error during execution of mode '{args.mode}': {main_exec_error}", exc_info=True)
        print(f"\n!!! Fatal execution error: {main_exec_error}. Check logs.", file=sys.stderr)
        final_status_ok = False; exit_code = 1
    finally:
        # --- 5. حفظ الحالة عند الخروج ---
        if engine:
            logger.info("Attempting to save system state...")
            try:
                engine.save_system_state()
                logger.info("System state saving initiated.")
            except Exception as e_save:
                logger.error(f"Error during system state saving: {e_save}", exc_info=True)

    # --- الخروج ---
    logger.info(f"Exiting application (Status: {'OK' if final_status_ok else 'Failed'}, Exit Code: {exit_code}).")
    sys.exit(exit_code)

if __name__ == "__main__":
    print("==================================================")
    print(" Starting OmniMind v1.0 Cognitive System ")
    print("==================================================")
    main_start_time = time.time()
    main() # استدعاء الوظيفة الرئيسية
    main_end_time = time.time()
    print("\n==================================================")
    print(f" OmniMind v1.0 Session Finished (Total Time: {main_end_time - main_start_time:.2f}s) ")
    print("==================================================")

# نهاية ملف main.py
