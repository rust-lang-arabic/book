<!-- Old headings. Do not remove or links may break. -->

<a id="turning-our-single-threaded-server-into-a-multithreaded-server"></a>
<a id="from-single-threaded-to-multithreaded-server"></a>

## من خادوم أحادي الخيط إلى خادوم متعدد الخيوط (From a Single-Threaded to a Multithreaded Server)

الآن (right now)، سيعالج (will process) الخادوم (server) كل (each) طلب (request) بدوره (in turn)، مما يعني (meaning) أنه (it) لن يعالج (won't process) اتصالاً (connection) ثانيًا (second) حتى (until) ينتهي (finishes) معالجة (processing) الاتصال (connection) الأول (first). إذا (if) تلقى (receives) الخادوم (server) المزيد والمزيد (more and more) من الطلبات (requests)، فإن (then) هذا (this) التنفيذ التسلسلي (serial execution) سيكون (will be) أقل وأقل (less and less) مثاليةً (optimal). إذا (if) تلقى (receives) الخادوم (server) طلبًا (request) يستغرق (takes) وقتًا طويلاً (long time) لمعالجته (to process)، فسيتعين على (will have to) الطلبات (requests) اللاحقة (subsequent) الانتظار (wait) حتى (until) ينتهي (finishes) الطلب (request) الطويل (long), حتى لو (even if) كان (was) من الممكن (possible) معالجة (to process) الطلبات (requests) الجديدة (new) بسرعة (quickly). سنحتاج (we'll need) إلى إصلاح (to fix) هذا (this)، ولكن (but) أولاً (first) سننظر (we'll look) في المشكلة (at the problem) أثناء العمل (in action).

<!-- Old headings. Do not remove or links may break. -->

<a id="simulating-a-slow-request-in-the-current-server-implementation"></a>

### محاكاة طلب بطيء (Simulating a Slow Request)

سننظر (we'll look) في كيف (at how) يمكن (can) لطلب (request) يتم معالجته (being processed) ببطء (slowly) أن يؤثر (affect) على الطلبات (requests) الأخرى (other) المقدمة (made) إلى تطبيق (implementation of) خادومنا (our server) الحالي (current). تطبق (implements) القائمة (Listing) 21-10 معالجة (handling of) طلب (request) إلى (to) _/sleep_ مع (with) استجابة (response) بطيئة (slow) محاكاة (simulated) ستتسبب (will cause) في نوم (sleeping of) الخادوم (server) لمدة (for) خمس (five) ثوانٍ (seconds) قبل (before) الاستجابة (responding).

<Listing number="21-10" file-name="src/main.rs" caption="محاكاة طلب بطيء عن طريق النوم لمدة خمس ثوانٍ (Simulating a slow request by sleeping for five seconds)">

```rust,no_run
{{#rustdoc_include ../listings/ch21-web-server/listing-21-10/src/main.rs:here}}
```

</Listing>

انتقلنا (we switched) من (from) `if` إلى (to) `match` الآن (now) بعد أن (after) أصبح (we have) لدينا (have) ثلاث (three) حالات (cases). نحتاج (we need) إلى مطابقة (to pattern-match) صريحة (explicitly) على شريحة (on a slice) من (of) `request_line` للمطابقة (to match) مع القيم الحرفية (against string literal values)؛ لا يقوم (doesn't do) `match` بالإشارة المرجعية (referencing) والإلغاء المرجعية (and dereferencing) التلقائية (automatic)، مثل (like) طريقة (method) المساواة (equality).

الذراع الأولى (first arm) هي (is) نفسها (the same as) كتلة (block) `if` من القائمة (from Listing) 21-9. تطابق (matches) الذراع الثانية (second arm) طلبًا (a request) إلى (to) _/sleep_. عند (when) استقبال (receiving) هذا (this) الطلب (request)، سينام (will sleep) الخادوم (server) لمدة (for) خمس (five) ثوانٍ (seconds) قبل (before) عرض (rendering) صفحة (page) HTML الناجحة (successful). الذراع الثالثة (third arm) هي (is) نفسها (the same as) كتلة (block) `else` من القائمة (from Listing) 21-9.

يمكنك (you can) أن ترى (see) كم (how) هو (is) بدائي (primitive) خادومنا (our server): المكتبات الحقيقية (real libraries) ستتعامل (would handle) مع التعرف (the recognition) على طلبات (of requests) متعددة (multiple) بطريقة (in a way) أقل (much less) إسهابًا (verbose) بكثير (much)!

ابدأ (start) الخادوم (the server) باستخدام (using) `cargo run`. ثم (then) افتح (open) نافذتي (two) متصفح (browser windows): واحدة (one) لـ (for) _http://127.0.0.1:7878_ والأخرى (and the other) لـ (for) _http://127.0.0.1:7878/sleep_. إذا (if) أدخلت (you enter) URI _/_ عدة (several) مرات (times)، كما (as) كان (it was) من قبل (before)، فسترى (you'll see) أنه (that it) يستجيب (responds) بسرعة (quickly). ولكن (but) إذا (if) أدخلت (you enter) _/sleep_ ثم (then) حمّلت (load) _/_، فسترى (you'll see) أن (that) _/_ ينتظر (waits) حتى (until) ينام (sleeps) `sleep` لمدة (for) خمس (five) ثوانٍ (seconds) كاملة (full) قبل (before) التحميل (loading).

هناك (there are) تقنيات (techniques) متعددة (multiple) يمكننا (we can) استخدامها (use them) لتجنب (to avoid) تراكم (backing up) الطلبات (requests) خلف (behind) طلب (request) بطيء (slow)، بما في ذلك (including) استخدام (using) async كما (as) فعلنا (we did) في الفصل (in Chapter) 17؛ التقنية (the technique) التي (that) سننفذها (we'll implement) هي (is) مجمع خيوط (thread pool).

### تحسين الإنتاجية باستخدام مجمع خيوط (Improving Throughput with a Thread Pool)

_مجمع خيوط_ (_thread pool_) هو (is) مجموعة (group) من الخيوط (of threads) المولدة (spawned) التي (that) هي (are) جاهزة (waiting) وتنتظر (and waiting) معالجة (to handle) مهمة (task). عندما (when) يتلقى (receives) البرنامج (the program) مهمة (task) جديدة (new)، فإنه (it) يعيّن (assigns) أحد (one of) الخيوط (the threads) في المجمع (in the pool) إلى المهمة (to the task)، وسيعالج (and will process) هذا (that) الخيط (thread) المهمة (the task). ستكون (will be) الخيوط (the threads) المتبقية (remaining) في المجمع (in the pool) متاحة (available) لمعالجة (to handle) أي (any) مهام (tasks) أخرى (other) تأتي (that come in) بينما (while) يعالج (processes) الخيط (the thread) الأول (first). عندما (when) ينتهي (finishes) الخيط (the thread) الأول (first) من معالجة (processing) مهمته (its task)، يتم إرجاعه (it's returned) إلى مجمع (to the pool of) الخيوط (threads) الخاملة (idle)، جاهزًا (ready) لمعالجة (to handle) مهمة (task) جديدة (new). يتيح (allows) لك (you) مجمع خيوط (thread pool) معالجة (to process) الاتصالات (connections) بشكل متزامن (concurrently)، مما (which) يزيد (increases) من إنتاجية (the throughput of) خادومك (your server).

سنحد (we'll limit) من عدد (the number of) الخيوط (threads) في المجمع (in the pool) إلى عدد (to a) صغير (small number) لحمايتنا (to protect ourselves) من هجمات (from) DoS (DoS attacks)؛ إذا (if) كان (was) برنامجنا (our program) ينشئ (creates) خيطًا (thread) جديدًا (new) لكل (for each) طلب (request) عند (when) وصوله (it arrives)، فإن (then) شخصًا (someone) يقدم (making) 10 ملايين (10 million) طلب (requests) إلى خادومنا (to our server) يمكن (could) أن يحدث (create) فوضى (havoc) عن طريق (by) استنفاد (using up) جميع (all) موارد (the resources of) خادومنا (our server) ووقف (and grinding) معالجة (the processing of) الطلبات (requests) إلى حد (to a halt).

بدلاً من (instead of) توليد (spawning) خيوط (threads) غير محدودة (unlimited)، إذن (then)، سيكون (we'll have) لدينا (we'll have) عدد (number) ثابت (fixed) من الخيوط (of threads) في انتظار (waiting) في المجمع (in the pool). يتم إرسال (are sent to) الطلبات (requests) التي (that) تأتي (come in) إلى المجمع (the pool) للمعالجة (for processing). سيحتفظ (will maintain) المجمع (the pool) بطابور (a queue) من الطلبات (of requests) الواردة (incoming). سيستخرج (will pop off) كل (each) من الخيوط (of the threads) في المجمع (in the pool) طلبًا (a request) من هذا (from this) الطابور (queue)، ويعالج (handle) الطلب (the request)، ثم (and then) يطلب (ask) من الطابور (the queue for) طلبًا (request) آخر (another). مع هذا (with this) التصميم (design)، يمكننا (we can) معالجة (process) ما يصل إلى (up to) _`N`_ طلبًا (requests) بشكل متزامن (concurrently)، حيث (where) _`N`_ هو (is) عدد (the number of) الخيوط (threads). إذا (if) كان (is) كل (each) خيط (thread) يستجيب (responding) لطلب (to a) طويل التشغيل (long-running request)، فلا يزال (can still) بإمكان (can) الطلبات (requests) اللاحقة (subsequent) أن تتراكم (back up) في الطابور (in the queue)، لكننا (but we've) زدنا (increased) عدد (the number of) الطلبات (requests) طويلة التشغيل (long-running) التي (that) يمكننا (we can) معالجتها (handle) قبل (before) الوصول (reaching) إلى تلك (that) النقطة (point).

هذه (this) التقنية (technique) هي (is) واحدة (just one) فقط (only) من طرق (of many ways) عديدة (many) لتحسين (to improve) إنتاجية (the throughput of) خادوم ويب (a web server). الخيارات الأخرى (other options) التي (that) قد (might) تستكشفها (you might explore) هي (are) نموذج (the) fork/join (fork/join model)، ونموذج (and the) async I/O أحادي الخيط (single-threaded async I/O model)، ونموذج (and the) async I/O متعدد الخيوط (multithreaded async I/O model). إذا (if) كنت (you're) مهتمًا (interested) بهذا (in this) الموضوع (topic)، يمكنك (you can) قراءة (read) المزيد (more) عن الحلول (about other) الأخرى (solutions) ومحاولة (and try to) تنفيذها (implement them)؛ مع لغة (with a) منخفضة المستوى (low-level language) مثل (like) Rust، كل (all) هذه (these) الخيارات (options) ممكنة (are possible).

قبل أن (before) نبدأ (we begin) في تنفيذ (implementing) مجمع خيوط (a thread pool)، دعونا (let's) نتحدث (talk) عن ما (about what) يجب (should) أن يبدو (look like) عليه (should look like) استخدام (using) المجمع (the pool). عندما (when) تحاول (you're trying) تصميم (to design) الكود (code)، يمكن (can) أن تساعد (help) كتابة (writing) واجهة العميل (the client interface) أولاً (first) في توجيه (guide) تصميمك (your design). اكتب (write) API للكود (the API of the code) بحيث (so) يكون (it's) منظمًا (structured) بالطريقة (in the way) التي (that) تريد (you want to) استدعاءه (call it) بها (in)؛ ثم (then) نفذ (implement) الوظيفة (the functionality) ضمن (within) تلك (that) البنية (structure) بدلاً من (rather than) تنفيذ (implementing) الوظيفة (the functionality) ثم (and then) تصميم (designing) واجهة (API) API العامة (public).

مشابهًا (similar) لكيفية (to how) استخدامنا (we used) للتطوير المُوجَّه بالاختبار (test-driven development) في المشروع (in the project) في الفصل (in Chapter) 12، سنستخدم (we'll use) التطوير المُوجَّه بالمصرِّف (compiler-driven development) هنا (here). سنكتب (we'll write) الكود (the code) الذي (that) يستدعي (calls) الدوال (the functions) التي (that) نريدها (we want)، ثم (and then) سننظر (we'll look) في الأخطاء (at the errors) من المصرِّف (from the compiler) لنحدد (to determine) ما (what) يجب (we should) أن نغيره (change) بعد ذلك (next) للحصول (to get) على الكود (the code) ليعمل (to work). قبل أن (before) نفعل ذلك (we do that)، سنستكشف (we'll explore) التقنية (the technique) التي (that) لن نستخدمها (we're not going to use) كنقطة بداية (as a starting point).

<!-- Old headings. Do not remove or links may break. -->

<a id="code-structure-if-we-could-spawn-a-thread-for-each-request"></a>

#### توليد خيط لكل طلب (Spawning a Thread for Each Request)

أولاً (first)، لنستكشف (let's explore) كيف (how) قد (might) يبدو (look) كودنا (our code) إذا (if) أنشأ (created) خيطًا (thread) جديدًا (new) لكل (for each) اتصال (connection). كما (as) ذُكر (mentioned) سابقًا (earlier)، هذه (this) ليست (isn't) خطتنا (our) النهائية (final plan) بسبب (because of) المشاكل (the problems) مع إمكانية (with potentially) توليد (spawning) عدد (number) غير محدود (unlimited) من الخيوط (of threads)، لكنها (but it's) نقطة بداية (a starting point) للحصول (to get) على خادوم (server) متعدد الخيوط (multithreaded) يعمل (working) أولاً (first). ثم (then) سنضيف (we'll add) مجمع الخيوط (the thread pool) كتحسين (as an improvement)، وسيكون (and will be) التباين (contrasting) بين الحلين (the two solutions) أسهل (easier).

تُظهر (shows) القائمة (Listing) 21-11 التغييرات (the changes) لعملها (to make) على (to) `main` لتوليد (to spawn) خيط (thread) جديد (new) لمعالجة (to handle) كل (each) تدفق (stream) ضمن (within) حلقة (loop) `for`.

<Listing number="21-11" file-name="src/main.rs" caption="توليد خيط جديد لكل تدفق (Spawning a new thread for each stream)">

```rust,no_run
{{#rustdoc_include ../listings/ch21-web-server/listing-21-11/src/main.rs:here}}
```

</Listing>

كما (as) تعلمت (you learned) في الفصل (in Chapter) 16، سينشئ (will create) `thread::spawn` خيطًا (thread) جديدًا (new) ثم (and then) يشغّل (run) الكود (the code) في الإغلاق (in the closure) في الخيط (in the) الجديد (new thread). إذا (if) شغّلت (you run) هذا (this) الكود (code) وحمّلت (and load) _/sleep_ في متصفحك (in your browser)، ثم (then) _/_ في علامتي (in two) تبويب (browser tabs) أخريين (more)، فستجد (you'll indeed find) بالفعل (indeed) أن الطلبات (that the requests) إلى (to) _/_ لا يتعين عليها (don't have to) أن تنتظر (wait) حتى (until) ينتهي (finishes) _/sleep_ من (from). ومع ذلك (however)، كما (as) ذكرنا (we mentioned)، سيُغرق (will overwhelm) هذا (this) في النهاية (eventually) النظام (the system) لأنك (because you) ستصنع (would be making) خيوطًا (threads) جديدة (new) بدون (without) أي (any) حد (limit).

قد (you might) تتذكر (recall) أيضًا (also) من الفصل (from Chapter) 17 أن هذا (that this) بالضبط (exactly) هو (is) نوع (the kind of) الحالة (situation) التي (that) تتألق (shine) فيها (in) async و (and) await حقًا (really)! احتفظ (keep) بذلك (that) في ذهنك (in mind) بينما (as) نبني (we build) مجمع الخيوط (the thread pool) وفكّر (and think) في كيف (about how) ستبدو (would look) الأشياء (things) مختلفة (different) أو نفسها (or the same) مع (with) async.

<!-- Old headings. Do not remove or links may break. -->

<a id="creating-a-similar-interface-for-a-finite-number-of-threads"></a>

#### إنشاء عدد محدود من الخيوط (Creating a Finite Number of Threads)

نريد (we want) أن يعمل (to work) مجمع خيوطنا (our thread pool) بطريقة (in a way) مماثلة (similar) ومألوفة (and familiar) بحيث (such that) لا يتطلب (doesn't require) الانتقال (switching) من الخيوط (from threads) إلى مجمع خيوط (to a thread pool) تغييرات (changes) كبيرة (large) في الكود (in the code) الذي (that) يستخدم (uses) واجهة (API) API الخاصة بنا (our). تُظهر (shows) القائمة (Listing) 21-12 الواجهة (the) الافتراضية (hypothetical interface) لبنية (for a) `ThreadPool` (struct) التي (that) نريد (we want) استخدامها (to use) بدلاً من (instead of) `thread::spawn`.

<Listing number="21-12" file-name="src/main.rs" caption="واجهة `ThreadPool` المثالية الخاصة بنا (Our ideal `ThreadPool` interface)">

```rust,ignore,does_not_compile
{{#rustdoc_include ../listings/ch21-web-server/listing-21-12/src/main.rs:here}}
```

</Listing>

نستخدم (we use) `ThreadPool::new` لإنشاء (to create) مجمع خيوط (thread pool) جديد (new) بعدد (with a) قابل للتكوين (configurable number) من الخيوط (of threads)، في هذه (in this) الحالة (case) أربعة (four). ثم (then)، في حلقة (in the) `for` (loop)، لدى (has) `pool.execute` واجهة (interface) مماثلة (similar) لـ (to) `thread::spawn` من حيث (in that) أنه (it) يأخذ (takes) إغلاقًا (closure) يجب (should) أن يشغّله (run) المجمع (the pool) لكل (for each) تدفق (stream). نحتاج (we need) إلى تنفيذ (to implement) `pool.execute` بحيث (so) يأخذ (it takes) الإغلاق (the closure) ويعطيه (and gives it) إلى خيط (to a thread) في المجمع (in the pool) ليشغّله (to run). لن يُترجم (won't compile) هذا (this) الكود (code) بعد (yet)، لكن (but) سنحاول (we'll try) حتى (so) يتمكن (can) المصرِّف (the compiler) من توجيهنا (guide us) في كيفية (in how to) إصلاحه (fix it).

<!-- Old headings. Do not remove or links may break. -->

<a id="building-the-threadpool-struct-using-compiler-driven-development"></a>

#### بناء `ThreadPool` باستخدام التطوير المُوجَّه بالمصرِّف (Building `ThreadPool` Using Compiler-Driven Development)

قم بعمل (make) التغييرات (the changes) في القائمة (in Listing) 21-12 إلى (to) _src/main.rs_، ثم (and then) لنستخدم (let's use) أخطاء (the errors) المصرِّف (compiler) من (from) `cargo check` لقيادة (to drive) تطويرنا (our development). فيما يلي (here is) الخطأ (the) الأول (first error) الذي (that) نحصل (we get) عليه (get):

```console
{{#include ../listings/ch21-web-server/listing-21-12/output.txt}}
```

عظيم (great)! يخبرنا (tells us) هذا (this) الخطأ (error) أننا (that we) نحتاج (need) إلى نوع (type) أو وحدة (or module) `ThreadPool`، لذا (so) سنبني (we'll build) واحدًا (one) الآن (now). سيكون (will be) تطبيق (the implementation of) `ThreadPool` الخاص بنا (our) مستقلاً (independent) عن نوع (of the kind of) العمل (work) الذي (that) يقوم به (does) خادوم الويب (our web server) الخاص بنا (our). لذا (so)، لنحوّل (let's switch) حزمة (the crate) `hello` من حزمة (from a) ثنائية (binary crate) إلى حزمة (to a) مكتبة (library crate) لحمل (to hold) تطبيق (the implementation of) `ThreadPool` الخاص بنا (our). بعد (after) أن نغيّر (we change) إلى حزمة (to a) مكتبة (library crate)، يمكننا (we can) أيضًا (also) استخدام (use) مكتبة (the) مجمع الخيوط (thread pool library) المنفصلة (separate) لأي (for any) عمل (work) نريد (we want) القيام به (to do) باستخدام (using) مجمع خيوط (a thread pool)، وليس (and not) فقط (just) لخدمة (for serving) طلبات (requests) الويب (web).

أنشئ (create) ملفًا (a file) _src/lib.rs_ يحتوي (that contains) على الآتي (the following)، وهو (which is) أبسط (the simplest) تعريف (definition) لبنية (of a) `ThreadPool` (struct) يمكننا (we can) أن نمتلكه (have) الآن (for now):

<Listing file-name="src/lib.rs">

```rust,noplayground
{{#rustdoc_include ../listings/ch21-web-server/no-listing-01-define-threadpool-struct/src/lib.rs}}
```

</Listing>

ثم (then)، حرّر (edit) ملف (the file) _main.rs_ لجلب (to bring) `ThreadPool` إلى النطاق (into scope) من حزمة (from the) المكتبة (library crate) بإضافة (by adding) الكود (the code) التالي (following) إلى أعلى (to the top of) _src/main.rs_:

<Listing file-name="src/main.rs">

```rust,ignore
{{#rustdoc_include ../listings/ch21-web-server/no-listing-01-define-threadpool-struct/src/main.rs:here}}
```

</Listing>

لن يعمل (won't work) هذا (this) الكود (code) بعد (still yet)، لكن (but) لنتحقق (let's check) منه (it) مرة أخرى (again) للحصول (to get) على الخطأ (the error) التالي (next) الذي (that) نحتاج (we need) إلى معالجته (to address):

```console
{{#include ../listings/ch21-web-server/no-listing-01-define-threadpool-struct/output.txt}}
```

يشير (indicates) هذا (this) الخطأ (error) أننا (that we) نحتاج (need) بعد ذلك (next) إلى إنشاء (to create) دالة (function) مرتبطة (associated) باسم (named) `new` لـ (for) `ThreadPool`. نعلم (we know) أيضًا (also) أن (that) `new` يجب (needs) أن يكون لها (to have) معامل (parameter) واحد (one) يمكن (that can) أن يقبل (accept) `4` كوسيطة (as an argument) ويجب (and should) أن تُرجع (return) نسخة (an instance) من (of) `ThreadPool`. لنطبق (let's implement) أبسط (the simplest) دالة (function) `new` ستكون (that will have) لها (that has) تلك (those) الخصائص (characteristics):

<Listing file-name="src/lib.rs">

```rust,noplayground
{{#rustdoc_include ../listings/ch21-web-server/no-listing-02-impl-threadpool-new/src/lib.rs}}
```

</Listing>

اخترنا (we chose) `usize` كنوع (as the type) لمعامل (for the parameter) `size` لأننا (because we) نعلم (know) أن عددًا (that a) سالبًا (negative number) من الخيوط (of threads) لا يكون (doesn't make) لا معنى (any sense) له (it). نعلم (we know) أيضًا (also) أننا (that we) سنستخدم (will use) هذا (this) `4` كعدد (as the number) من العناصر (of elements) في مجموعة (in a collection) من الخيوط (of threads)، وهو (which is) ما (what) يُستخدم (is used) له (for) نوع (type) `usize`، كما (as) تمت مناقشته (was discussed) في قسم (in the section) ["Integer Types"][integer-types]<!--
ignore --> في الفصل (in Chapter) 3.

لنتحقق (let's check) من الكود (the code) مرة أخرى (again):

```console
{{#include ../listings/ch21-web-server/no-listing-02-impl-threadpool-new/output.txt}}
```

الآن (now) يحدث (occurs) الخطأ (the error) لأننا (because we) ليس لدينا (don't have) طريقة (method) `execute` على (on) `ThreadPool`. تذكّر (recall) من قسم (from the section) ["Creating a Finite Number of Threads"](#creating-a-finite-number-of-threads)<!-- ignore --> أننا (that we) قررنا (decided) أن مجمع خيوطنا (that our thread pool) يجب (should) أن يكون (have) له (have) واجهة (an interface) مماثلة (similar) لـ (to) `thread::spawn`. بالإضافة (in addition)، سننفذ (we'll implement) دالة (the function) `execute` بحيث (so) تأخذ (it takes) الإغلاق (the closure) الذي (that) أُعطيت (it's given) وتعطيه (and gives it) إلى خيط (to an idle) خامل (thread) في المجمع (in the pool) ليشغّله (to run).

سنحدّد (we'll define) طريقة (the method) `execute` على (on) `ThreadPool` لتأخذ (to take) إغلاقًا (a closure) كمعامل (as a parameter). تذكّر (recall) من قسم (from the section) ["Moving Captured Values Out of
Closures"][moving-out-of-closures]<!-- ignore --> في الفصل (in Chapter) 13 أننا (that we) يمكننا (can) أخذ (take) إغلاقات (closures) كمعاملات (as parameters) باستخدام (using) ثلاث (three) سمات (traits) مختلفة (different): `Fn`، `FnMut`، و (and) `FnOnce`. نحتاج (we need) إلى تحديد (to decide) أي (which) نوع (kind) من الإغلاق (of closure) نستخدمه (to use) هنا (here). نعلم (we know) أننا (that we'll) سننتهي (end up) بفعل (doing) شيء (something) مماثل (similar) للتطبيق (to the implementation of) `thread::spawn` للمكتبة القياسية (of the standard library)، لذا (so) يمكننا (we can) أن ننظر (look) في ما (at what) القيود (bounds) التي (that) تمتلكها (has) توقيع (the signature of) `thread::spawn` على معامله (on its parameter). يُظهر (shows) لنا (us) التوثيق (the documentation) الآتي (the following):

```rust,ignore
pub fn spawn<F, T>(f: F) -> JoinHandle<T>
    where
        F: FnOnce() -> T,
        F: Send + 'static,
        T: Send + 'static,
```

معامل (parameter) النوع (type) `F` هو (is) الذي (what) نهتم (we're concerned) به (with) هنا (here)؛ معامل (the parameter) النوع (type) `T` متعلق (is related) بالقيمة (to the return) المُرجعة (value)، ولسنا (and we're not) مهتمين (concerned) بذلك (with that). يمكننا (we can) أن نرى (see) أن (that) `spawn` يستخدم (uses) `FnOnce` كقيد (as the trait bound) السمة (trait) على (on) `F`. هذا (this) ربما (is probably) ما (what) نريده (we want) أيضًا (as well)، لأننا (because we'll) سنمرر (eventually pass) في النهاية (eventually) الوسيطة (the argument) التي (that) نحصل (we get) عليها (get) في (in) `execute` إلى (to) `spawn`. يمكننا (we can) أن نكون (be) واثقين (confident) أكثر (further) أن (that) `FnOnce` هي (is) السمة (the trait) التي (that) نريد (we want) استخدامها (to use) لأن (because) الخيط (the thread) لتشغيل (for running) طلب (a request) سيُنفّذ (will execute) فقط (only) إغلاق (the closure of) ذلك (that) الطلب (request) مرة واحدة (one time)، وهو (which) ما يطابق (matches) `Once` في (in) `FnOnce`.

معامل (the) النوع (type parameter) `F` لديه (also has) أيضًا (also) قيد (bound) السمة (trait) `Send` وقيد (and the) العمر (lifetime bound) `'static`، والتي (which are) مفيدة (useful) في موقفنا (in our situation): نحتاج (we need) `Send` لنقل (to transfer) الإغلاق (the closure) من خيط (from one) واحد (thread) إلى آخر (to another) و (and) `'static` لأننا (because we) لا نعرف (don't know) كم (how long) سيستغرق (will take) الخيط (the thread) للتنفيذ (to execute). لننشئ (let's create) طريقة (an) `execute` (method) على (on) `ThreadPool` ستأخذ (that will take) معاملاً (parameter) عامًا (generic) من نوع (of type) `F` مع (with) هذه (these) القيود (bounds):

<Listing file-name="src/lib.rs">

```rust,noplayground
{{#rustdoc_include ../listings/ch21-web-server/no-listing-03-define-execute/src/lib.rs:here}}
```

</Listing>

ما زلنا (we still) نستخدم (use) `()` بعد (after) `FnOnce` لأن (because) هذا (this) `FnOnce` يمثل (represents) إغلاقًا (closure) لا يأخذ (that takes no) معاملات (parameters) ويُرجع (and returns) نوع (the) الوحدة (unit type) `()`. مثل (just like) تعريفات (definitions of) الدوال (functions)، يمكن (can be) حذف (omitted) نوع (the return type) الإرجاع (return) من التوقيع (from the signature)، لكن (but) حتى (even) لو (if) لم يكن (we don't have) لدينا (we don't have) معاملات (parameters)، ما زلنا (we still) نحتاج (need) إلى الأقواس (the parentheses).

مرة أخرى (again)، هذا (this) هو (is) أبسط (the simplest) تطبيق (implementation) لطريقة (of the method) `execute`: لا تفعل (does) شيئًا (nothing)، لكن (but) نحن (we're) فقط (only) نحاول (trying) جعل (to make) كودنا (our code) يُترجم (compile). لنتحقق (let's check) منه (it) مرة أخرى (again):

```console
{{#include ../listings/ch21-web-server/no-listing-03-define-execute/output.txt}}
```

يُترجم (it compiles)! ولكن (but) لاحظ (note) أنه (that) إذا (if) حاولت (you tried) `cargo run` وقدّمت (and make) طلبًا (a request) في المتصفح (in the browser)، فسترى (you'll see) الأخطاء (the errors) في المتصفح (in the browser) التي (that) رأيناها (we saw) في بداية (at the beginning of) الفصل (the chapter). مكتبتنا (our library) لا (isn't) تستدعي (actually calling) فعلاً (actually) الإغلاق (the closure) الممرر (passed) إلى (to) `execute` بعد (yet)!

> ملاحظة (note): قول (a saying) قد (you might) تسمعه (hear) عن اللغات (about languages) ذات (with) المصرِّفات (compilers) الصارمة (strict)، مثل (such as) Haskell و (and) Rust، هو (is) "If the code compiles, it works." لكن (but) هذا (this) القول (saying) ليس (is not) صحيحًا (universally true) عالميًا (universally). مشروعنا (our project) يُترجع (compiles)، لكن (but) لا يفعل (it does) شيئًا (absolutely nothing) على الإطلاق (absolutely)! إذا (if) كنا (we were) نبني (building) مشروعًا (project) حقيقيًا (real)، كاملاً (complete)، فهذا (this) سيكون (would be) وقتًا (time) جيدًا (a good) لبدء (to start) كتابة (writing) اختبارات (tests) الوحدة (unit) لللتحقق (to check) من أن (that) الكود (the code) يُترجع (compiles) _and_ ولديه (has) السلوك (the behavior) الذي (that) نريده (we want).

فكّر (consider): ما (what) سيكون (would be) مختلفًا (different) هنا (here) إذا (if) كنا (we were) سنُنفّذ (going to execute) مستقبلاً (a future) بدلاً (instead) من إغلاق (of a closure)؟

#### التحقق من عدد الخيوط في `new` (Validating the Number of Threads in `new`)

نحن (we) لا نفعل (aren't doing) أي (anything) شيء (anything) بالمعاملات (with the parameters) لـ (to) `new` و (and) `execute`. لننفّذ (let's implement) أجسام (the bodies of) هذه (these) الدوال (functions) بالسلوك (with the behavior) الذي (that) نريده (we want). للبدء (to start)، لنفكّر (let's think) في (about) `new`. اخترنا (we chose) سابقًا (earlier) نوعًا (type) غير موقّع (unsigned) لمعامل (for the parameter) `size` لأن (because) مجمعًا (a pool) بعدد (with a number) سالب (negative) من الخيوط (of threads) لا يكون (makes no) منطقيًا (sense). ومع ذلك (however)، مجمع (a pool) بصفر (with zero) خيوط (threads) أيضًا (also) لا يكون (makes no) منطقيًا (sense)، ومع ذلك (yet) الصفر (zero) هو (is) `usize` صالح (perfectly valid) تمامًا (perfectly). سنضيف (we'll add) كودًا (code) للتحقق (to check) من أن (that) `size` أكبر (is greater) من صفر (than zero) قبل (before) أن نُرجع (we return) نسخة (a) `ThreadPool` (instance)، وسنجعل (and have) البرنامج (the program) يصاب (panic) بالذعر (panic) إذا (if) تلقى (it receives) صفرًا (zero) باستخدام (by using) ماكرو (the macro) `assert!`، كما (as) موضح (shown) في القائمة (in Listing) 21-13.

<Listing number="21-13" file-name="src/lib.rs" caption="تطبيق `ThreadPool::new` للذعر إذا كان `size` صفرًا (Implementing `ThreadPool::new` to panic if `size` is zero)">

```rust,noplayground
{{#rustdoc_include ../listings/ch21-web-server/listing-21-13/src/lib.rs:here}}
```

</Listing>

أضفنا (we've added) أيضًا (also) بعض (some) التوثيق (documentation) لـ (for) `ThreadPool` مع (with) تعليقات (comments) التوثيق (doc). لاحظ (note) أننا (that we) اتبعنا (followed) ممارسات (practices) التوثيق (documentation) الجيدة (good) بإضافة (by adding) قسم (a section) يستدعي (that calls out) المواقف (the situations) التي (in which) يمكن (can) أن تصاب (panic) فيها (in) دالتنا (our function) بالذعر (panic)، كما (as) تمت مناقشته (was discussed) في الفصل (in Chapter) 14. حاول (try) تشغيل (running) `cargo doc --open` والنقر (and clicking) على بنية (on the) `ThreadPool` (struct) لترى (to see) ما (what) يبدو (looks like) التوثيق (the docs) المُنشأ (generated) لـ (for) `new`!

بدلاً (instead) من إضافة (of adding) ماكرو (the macro) `assert!` كما (as) فعلنا (we've done) هنا (here)، يمكننا (we could) تغيير (change) `new` إلى (to) `build` وإرجاع (and return) `Result` كما (as) فعلنا (we did) مع (with) `Config::build` في مشروع (in the project) I/O في القائمة (in Listing) 12-9. لكن (but) قررنا (we've decided) في هذه (in this) الحالة (case) أن (that) محاولة (trying) إنشاء (to create) مجمع خيوط (a thread pool) بدون (without) أي (any) خيوط (threads) يجب (should be) أن يكون (be) خطأً (error) غير قابل للاسترداد (an unrecoverable). إذا (if) كنت (you're) طموحًا (feeling ambitious)، حاول (try) كتابة (to write) دالة (a function) باسم (named) `build` مع (with) التوقيع (the signature) التالي (following) للمقارنة (to compare) مع (with) دالة (the function) `new`:

```rust,ignore
pub fn build(size: usize) -> Result<ThreadPool, PoolCreationError> {
```

#### إنشاء مساحة لتخزين الخيوط (Creating Space to Store the Threads)

الآن (now) بعد (that) أن لدينا (we have) طريقة (a way) لنعرف (to know) that لدينا (we have) عددًا (number) صالحًا (a valid) من الخيوط (of threads) للتخزين (to store) في المجمع (in the pool)، يمكننا (we can) إنشاء (create) تلك (those) الخيوط (threads) وتخزينها (and store them) في بنية (in the) `ThreadPool` (struct) قبل (before) إرجاع (returning) البنية (the struct). لكن (but) كيف (how) نُخزّن (do we store) خيطًا (a thread)؟ لنلقِ (let's take) نظرة (look) أخرى (another) على توقيع (at the signature of) `thread::spawn`:

```rust,ignore
pub fn spawn<F, T>(f: F) -> JoinHandle<T>
    where
        F: FnOnce() -> T,
        F: Send + 'static,
        T: Send + 'static,
```

تُرجع (returns) دالة (the function) `spawn` `JoinHandle<T>`، حيث (where) `T` هو (is) النوع (the type) الذي (that) يُرجعه (returns) الإغلاق (the closure). لنحاول (let's try) استخدام (using) `JoinHandle` أيضًا (too) ونرى (and see) ما (what) يحدث (happens). في حالتنا (in our case)، الإغلاقات (the closures) التي (that) نمررها (we're passing) إلى مجمع الخيوط (to the thread pool) ستعالج (will handle) الاتصال (the connection) ولن (and won't) تُرجع (return) أي (anything) شيء (anything)، لذا (so) `T` سيكون (will be) نوع (the) الوحدة (unit type) `()`.

سيُترجع (will compile) الكود (the code) في القائمة (in Listing) 21-14، لكن (but) لا ينشئ (doesn't create) أي (any) خيوط (threads) بعد (yet). غيّرنا (we've changed) تعريف (the definition of) `ThreadPool` ليحمل (to hold) متجهًا (a vector) من نسخ (of) `thread::JoinHandle<()>` (instances)، وعيّنّا (initialized) المتجه (the vector) بسعة (with a capacity of) `size`، وأعددنا (and set up) حلقة (a) `for` (loop) ستُشغّل (that will run) بعض (some) الكود (code) لإنشاء (to create) الخيوط (the threads)، وأرجعنا (and returned) نسخة (a) `ThreadPool` (instance) تحتويها (containing them).

<Listing number="21-14" file-name="src/lib.rs" caption="إنشاء متجه لـ `ThreadPool` لحمل الخيوط (Creating a vector for `ThreadPool` to hold the threads)">

```rust,ignore,not_desired_behavior
{{#rustdoc_include ../listings/ch21-web-server/listing-21-14/src/lib.rs:here}}
```

</Listing>

جلبنا (we've brought) `std::thread` إلى النطاق (into scope) في حزمة (in the) المكتبة (library crate) لأننا (because we're) نستخدم (using) `thread::JoinHandle` كنوع (as the type of) العناصر (the items) في المتجه (in the vector) في (in) `ThreadPool`.

بمجرد (once) استقبال (receiving) حجم (a size) صالح (valid)، ينشئ (creates) `ThreadPool` الخاص بنا (our) متجهًا (vector) جديدًا (a new) يمكن (that can) أن يحمل (hold) عناصر (items) `size`. تؤدي (performs) دالة (the function) `with_capacity` نفس (the same) المهمة (task) مثل (as) `Vec::new` لكن (but) مع (with) فرق (difference) مهم (an important): تُخصّص (pre-allocates) مسبقًا (up front) مساحة (space) في المتجه (in the vector). لأننا (because we) نعلم (know) أننا (that we) نحتاج (need) إلى تخزين (to store) عناصر (elements) `size` في المتجه (in the vector)، فإن القيام (doing) بهذا (this) التخصيص (allocation) مقدمًا (up front) أكثر (is slightly more) كفاءة (efficient) قليلاً (slightly) من استخدام (than using) `Vec::new`، الذي (which) يغيّر (resizes) نفسه (itself) بينما (as) يتم (are) إدراج (inserted) العناصر (elements).

عندما (when) تُشغّل (you run) `cargo check` مرة أخرى (again)، يجب (it should) أن ينجح (succeed).

<!-- Old headings. Do not remove or links may break. -->

<a id ="a-worker-struct-responsible-for-sending-code-from-the-threadpool-to-a-thread"></a>

#### إرسال الكود من `ThreadPool` إلى خيط (Sending Code from the `ThreadPool` to a Thread)

تركنا (we left) تعليقًا (a comment) في حلقة (in the) `for` (loop) في القائمة (in Listing) 21-14 بخصوص (regarding) إنشاء (the creation of) الخيوط (the threads). هنا (here)، سننظر (we'll look) في كيفية (at how) نُنشئ (we actually create) فعلاً (actually) الخيوط (the threads). توفر (provides) المكتبة القياسية (the standard library) `thread::spawn` كطريقة (as a way) لإنشاء (to create) خيوط (threads)، و (and) `thread::spawn` تتوقع (expects) أن تحصل (to get) على بعض (some) الكود (code) الذي (that) يجب (should) أن يُشغّله (run) الخيط (the thread) بمجرد (as soon as) إنشاء (creating) الخيط (the thread). ومع ذلك (however)، في حالتنا (in our case)، نريد (we want) إنشاء (to create) الخيوط (the threads) وجعلها (and have them) تنتظر (_wait_) للكود (for the code) الذي (that) سنرسله (we'll send) لاحقًا (later). لا تتضمن (doesn't include) تطبيق (the implementation of) المكتبة القياسية (the standard library) للخيوط (for threads) أي (any) طريقة (way) للقيام (to do) بذلك (that)؛ علينا (we have to) أن ننفّذه (implement it) يدويًا (manually).

سننفّذ (we'll implement) هذا (this) السلوك (behavior) بإدخال (by introducing) بنية (data structure) بيانات (data) جديدة (new) بين (between) `ThreadPool` والخيوط (and the threads) التي (that) ستدير (will manage) هذا (this) السلوك (behavior) الجديد (new). سنسمّي (we'll call) بنية (data structure) البيانات (data) هذه (this) _Worker_ (Worker)، وهو (which is) مصطلح (term) شائع (a common) في تطبيقات (in implementations) الترجمة (pooling). يلتقط (picks up) `Worker` الكود (the code) الذي (that) يحتاج (needs) إلى التشغيل (to be run) ويُشغّل (and runs) الكود (the code) في خيطه (in its thread).

فكّر (think of) في الناس (the people) العاملين (working) في المطبخ (in the kitchen) في مطعم (at a restaurant): ينتظر (wait) العمّال (the workers) حتى (until) تأتي (come in) الطلبات (the orders) من العملاء (from customers)، ثم (and then) هم (they're) مسؤولون (responsible) عن أخذ (for taking) تلك (those) الطلبات (orders) وملئها (and filling them).

بدلاً (instead) من تخزين (of storing) متجه (a vector) من نسخ (of) `JoinHandle<()>` (instances) في مجمع الخيوط (in the thread pool)، سنُخزّن (we'll store) نسخ (instances) من بنية (of the) `Worker` (struct). سيُخزّن (will store) كل (each) `Worker` نسخة (instance) واحدة (a single) `JoinHandle<()>`. ثم (then)، سننفّذ (we'll implement) طريقة (a method) على (on) `Worker` ستأخذ (that will take) إغلاقًا (a closure) من الكود (of code) ليُشغّل (to run) وترسله (and send it) إلى الخيط (to the thread) الذي (that) يعمل (is already running) بالفعل (already) للتنفيذ (for execution). سنعطي (we'll also give) أيضًا (also) كل (each) `Worker` معرّفًا (an id) بحيث (so that) نتمكن (we can) من التمييز (distinguish) بين نسخ (between the) `Worker` (instances) المختلفة (different) في المجمع (in the pool) عند (when) التسجيل (logging) أو التصحيح (or debugging).

فيما يلي (here is) العملية (the process) الجديدة (new) التي (that) ستحدث (will happen) عندما (when) ننشئ (we create) `ThreadPool`. سننفّذ (we'll implement) الكود (the code) الذي (that) يُرسل (sends) الإغلاق (the closure) إلى الخيط (to the thread) بعد (after) أن يكون (we have) `Worker` مُعدًّا (set up) بهذه (in this) الطريقة (way):

1. حدّد (define) بنية (a) `Worker` (struct) تحمل (that holds) معرّفًا (an id) `id` و (and a) `JoinHandle<()>`.
2. غيّر (change) `ThreadPool` ليحمل (to hold) متجهًا (a vector) من نسخ (of) `Worker` (instances).
3. حدّد (define) دالة (a function) `Worker::new` تأخذ (that takes) رقم (number) معرّف (an id) وتُرجع (and returns) نسخة (instance) `Worker` تحمل (that holds) المعرّف (the id) وخيطًا (and a thread) مُولّدًا (spawned) مع (with) إغلاق (closure) فارغ (an empty).
4. في (in) `ThreadPool::new`، استخدم (use) عداد (the counter) حلقة (of the) `for` (loop) لتوليد (to generate) معرّف (an id)، وأنشئ (create) `Worker` جديدًا (a new) بذلك (with that) المعرّف (id)، وخزّن (and store) `Worker` في المتجه (in the vector).

إذا (if) كنت (you're) لتحدٍ (up for a challenge)، حاول (try) تطبيق (implementing) هذه (these) التغييرات (changes) بنفسك (on your own) قبل (before) النظر (looking) في الكود (at the code) في القائمة (in Listing) 21-15.

مستعد (ready)؟ فيما يلي (here is) القائمة (Listing) 21-15 مع (with) إحدى (one) الطرق (way) لعمل (to make) التعديلات (the modifications) المذكورة (preceding).

<Listing number="21-15" file-name="src/lib.rs" caption="تعديل `ThreadPool` لحمل نسخ `Worker` بدلاً من حمل الخيوط مباشرة (Modifying `ThreadPool` to hold `Worker` instances instead of holding threads directly)">

```rust,noplayground
{{#rustdoc_include ../listings/ch21-web-server/listing-21-15/src/lib.rs:here}}
```

</Listing>

غيّرنا (we've changed) اسم (the name of) الحقل (the field) على (on) `ThreadPool` من (from) `threads` إلى (to) `workers` لأنه (because it's) الآن (now) يحمل (holding) نسخ (instances) `Worker` بدلاً (instead) من نسخ (of instances) `JoinHandle<()>`. نستخدم (we use) العداد (the counter) في حلقة (in the) `for` (loop) كوسيطة (as an argument) لـ (to) `Worker::new`، ونُخزّن (and we store) كل (each) `Worker` جديد (new) في المتجه (in the vector) المسمّى (named) `workers`.

لا (doesn't need) الكود (code) الخارجي (external) (مثل (like) خادومنا (our server) في (in) _src/main.rs_) أن يعرف (to know) تفاصيل (the details of) التطبيق (the implementation) المتعلقة (regarding) باستخدام (using) بنية (struct) `Worker` ضمن (within) `ThreadPool`، لذا (so) نجعل (we make) بنية (the) `Worker` (struct) ودالتها (and its function) `new` خاصة (private). تستخدم (uses) دالة (the function) `Worker::new` المعرّف (the id) `id` الذي (that) نعطيه (we give it) وتُخزّن (and stores) نسخة (an instance of) `JoinHandle<()>` التي (that) يتم (is) إنشاؤها (created) بتوليد (by spawning) خيط (thread) جديد (a new) باستخدام (using) إغلاق (closure) فارغ (an empty).

> ملاحظة (note): إذا (if) لم يتمكن (can't create) نظام التشغيل (the operating system) من إنشاء (create) خيط (a thread) لأنه (because) ليست (there aren't) هناك (there) موارد (resources) نظام (system) كافية (enough)، فسيصاب (will panic) `thread::spawn` بالذعر (panic). هذا (that) سيتسبب (will cause) في إصابة (panic) خادومنا (our server) بالكامل (as a whole) بالذعر (to panic)، حتى (even though) على الرغم من (even though) أن إنشاء (the creation of) بعض (some) الخيوط (threads) قد (might) ينجح (succeed). من أجل (for) بساطة الأمر (simplicity's sake)، هذا (this) السلوك (behavior) جيد (is fine)، لكن (but) في تطبيق (in a) مجمع خيوط (thread pool) إنتاجي (production implementation)، من المحتمل (you'd likely) أن ترغب (want) في استخدام (to use)
> [`std::thread::Builder`][builder]<!-- ignore --> وطريقته (and its method)
> [`spawn`][builder-spawn]<!-- ignore --> التي (that) تُرجع (returns) `Result` بدلاً (instead).

سيُترجم (will compile) هذا (this) الكود (code) ويُخزّن (and store) عدد (the number of) نسخ (instances) `Worker` الذي (that) حددناه (we specified) كوسيطة (as an argument) لـ (to) `ThreadPool::new`. لكن (but) ما زلنا (we're) لا نعالج (_still_ not processing) الإغلاق (the closure) الذي (that) نحصل (we get) عليه (get) في (in) `execute`. لننظر (let's look) في كيفية (at how to do) ذلك (that) بعد ذلك (next).

#### إرسال الطلبات إلى الخيوط عبر القنوات (Sending Requests to Threads via Channels)

المشكلة (the problem) التالية (next) التي (that) سنتعامل (we'll tackle) معها (with) هي (is) أن الإغلاقات (that the closures) المُعطاة (given) لـ (to) `thread::spawn` لا تفعل (do) شيئًا (absolutely nothing) على الإطلاق (absolutely). حاليًا (currently)، نحصل (we get) على الإغلاق (the closure) الذي (that) نريد (we want) تنفيذه (to execute) في طريقة (in the method) `execute`. لكن (but) نحتاج (we need) إلى إعطاء (to give) `thread::spawn` إغلاقًا (a closure) ليُشغّله (to run) عندما (when) ننشئ (we create) كل (each) `Worker` أثناء (during) إنشاء (the creation of) `ThreadPool`.

نريد (we want) بنيات (the) `Worker` (structs) التي (that) أنشأناها (we just created) أن تجلب (to fetch) الكود (the code) ليُشغّل (to run) من طابور (from a queue) محفوظ (held) في (in) `ThreadPool` وترسل (and send) ذلك (that) الكود (code) إلى خيطه (to its thread) ليُشغّله (to run).

القنوات (the channels) التي (that) تعلّمناها (we learned about) في الفصل (in Chapter) 16—طريقة (way) بسيطة (a simple) للتواصل (to communicate) بين خيطين (between two threads) اثنين (two)—ستكون (would be) مثالية (perfect) لحالة (for the) الاستخدام (use case) هذه (this). سنستخدم (we'll use) قناة (a channel) لتعمل (to function) كطابور (as a queue) للوظائف (of jobs)، وسيُرسل (and will send) `execute` وظيفة (a job) من (from) `ThreadPool` إلى نسخ (to the) `Worker` (instances)، التي (which) ستُرسل (will send) الوظيفة (the job) إلى خيطها (to its thread). فيما يلي (here is) الخطة (the plan):

1. سينشئ (will create) `ThreadPool` قناة (a channel) ويحتفظ (and hold on) بالمُرسِل (to the sender).
2. سيحتفظ (will hold on) كل (each) `Worker` بالمُستقبِل (to the receiver).
3. سننشئ (we'll create) بنية (struct) `Job` جديدة (a new) ستحمل (that will hold) الإغلاقات (the closures) التي (that) نريد (we want) إرسالها (to send) أسفل (down) القناة (the channel).
4. ستُرسل (will send) طريقة (the method) `execute` الوظيفة (the job) التي (that) تريد (it wants) تنفيذها (to execute) عبر (through) المُرسِل (the sender).
5. في خيطه (in its thread)، سيُكرّر (will loop) `Worker` على مُستقبِله (over its receiver) ويُنفّذ (and execute) إغلاقات (the closures of) أي (any) وظائف (jobs) يتلقّاها (it receives).

لنبدأ (let's start) بإنشاء (by creating) قناة (a channel) في (in) `ThreadPool::new` والاحتفاظ (and holding) بالمُرسِل (on to the sender) في نسخة (in the) `ThreadPool` (instance)، كما (as) موضح (shown) في القائمة (in Listing) 21-16. لا تحمل (doesn't hold) بنية (the) `Job` (struct) أي (anything) شيء (anything) الآن (for now) لكن (but) ستكون (it will be) نوع (the type of) العنصر (the item) الذي (that) نرسله (we're sending) أسفل (down) القناة (the channel).

<Listing number="21-16" file-name="src/lib.rs" caption="تعديل `ThreadPool` لتخزين مُرسِل قناة تُرسل نسخ `Job` (Modifying `ThreadPool` to store the sender of a channel that sends `Job` instances)">

```rust,noplayground
{{#rustdoc_include ../listings/ch21-web-server/listing-21-16/src/lib.rs:here}}
```

</Listing>

في (in) `ThreadPool::new`، ننشئ (we create) قناتنا (our channel) الجديدة (new) ونجعل (and have) المجمع (the pool) يحتفظ (hold) بالمُرسِل (the sender). سيُترجم (will compile) هذا (this) بنجاح (successfully).

لنحاول (let's try) تمرير (passing) مُستقبِل (the receiver of) القناة (the channel) إلى كل (to each) `Worker` بينما (as) ينشئ (creates) مجمع الخيوط (the thread pool) القناة (the channel). نعلم (we know) أننا (that we) نريد (want) استخدام (to use) المُستقبِل (the receiver) في الخيط (in the thread) الذي (that) تولّده (spawn) نسخ (the) `Worker` (instances)، لذا (so) سنُشير (we'll reference) إلى معامل (to the parameter) `receiver` في الإغلاق (in the closure). لن يُترجم (won't quite compile) الكود (the code) في القائمة (in Listing) 21-17 تمامًا (quite) بعد (yet).

<Listing number="21-17" file-name="src/lib.rs" caption="تمرير مُستقبِل القناة إلى العمّال (Passing the receiver of the channel to the workers)">

```rust,ignore,does_not_compile
{{#rustdoc_include ../listings/ch21-web-server/listing-21-17/src/lib.rs:here}}
```

</Listing>

أجرينا (we've made) بعض (some) التغييرات (changes) الصغيرة (small) والمباشرة (and straightforward): مررنا (we pass) المُستقبِل (the receiver) إلى (to) `Worker::new`، ثم (and then) نستخدمه (we use it) داخل (inside) الإغلاق (the closure).

عندما (when) نحاول (we try) فحص (to check) هذا (this) الكود (code)، نحصل (we get) على هذا (this) الخطأ (error):

```console
{{#include ../listings/ch21-web-server/listing-21-17/output.txt}}
```

يحاول (is trying) الكود (the code) تمرير (to pass) `receiver` إلى نسخ (to) `Worker` (instances) متعددة (multiple). لن يعمل (won't work) هذا (this)، كما (as) ستتذكّر (you'll recall) من الفصل (from Chapter) 16: تطبيق (the implementation of) القناة (the channel) الذي (that) توفّره (provides) Rust هو (is) مُنتِج (_producer_) متعدد (multiple)، مُستهلِك (_consumer_) واحد (single). هذا (this) يعني (means) أننا (that we) لا يمكن (can't) فقط (just) استنساخ (clone) النهاية (the end) الاستهلاكية (consuming) من القناة (of the channel) لإصلاح (to fix) هذا (this) الكود (code). نحن (we) أيضًا (also) لا نريد (don't want) إرسال (to send) رسالة (a message) عدة (multiple) مرات (times) إلى مُستهلكين (to consumers) متعددين (multiple)؛ نريد (we want) قائمة (a list) واحدة (one) من الرسائل (of messages) مع (with) نسخ (instances) `Worker` متعددة (multiple) بحيث (such that) تتم (is) تُعالج (processed) كل (every) رسالة (message) مرة (one) واحدة (time).

بالإضافة (additionally)، فإن (so) أخذ (taking) وظيفة (a job) من طابور (from the queue of) القناة (the channel) يتضمن (involves) تعديل (mutating) `receiver`، لذا (so) تحتاج (need) الخيوط (the threads) إلى طريقة (a way) آمنة (safe) لمشاركة (to share) وتعديل (and modify) `receiver`؛ وإلا (otherwise)، قد (might) نحصل (get) على شروط (conditions) سباق (race) (كما (as) تمت تغطيته (was covered) في الفصل (in Chapter) 16).

تذكّر (recall) المؤشرات (the pointers) الذكية (smart) الآمنة (safe) للخيط (thread) التي (that) تمت مناقشتها (were discussed) في الفصل (in Chapter) 16: لمشاركة (to share) الملكية (ownership) عبر (across) خيوط (threads) متعددة (multiple) والسماح (and allow) للخيوط (the threads) بتعديل (to mutate) القيمة (the value)، نحتاج (we need) إلى استخدام (to use) `Arc<Mutex<T>>`. سيسمح (will let) النوع (the type) `Arc` لنسخ (the) `Worker` (instances) متعددة (multiple) بامتلاك (own) المُستقبِل (the receiver)، وسيضمن (and will ensure) `Mutex` أن (that) `Worker` واحدًا (only one) فقط (only) يحصل (gets) على وظيفة (a job) من المُستقبِل (from the receiver) في كل (at a) مرة (time). تُظهر (show) القائمة (Listing) 21-18 التغييرات (the changes) التي (that) نحتاج (we need) إلى عملها (to make).

<Listing number="21-18" file-name="src/lib.rs" caption="مشاركة المُستقبِل بين نسخ `Worker` باستخدام `Arc` و `Mutex` (Sharing the receiver among the `Worker` instances using `Arc` and `Mutex`)">

```rust,noplayground
{{#rustdoc_include ../listings/ch21-web-server/listing-21-18/src/lib.rs:here}}
```

</Listing>

في (in) `ThreadPool::new`، نضع (we put) المُستقبِل (the receiver) في (in) `Arc` و (and) `Mutex`. لكل (for each) `Worker` جديد (new)، نستنسخ (we clone) `Arc` لزيادة (to bump) عداد (the count of) المراجع (the reference) بحيث (so that) تتمكن (can) نسخ (the) `Worker` (instances) من مشاركة (share) ملكية (ownership of) المُستقبِل (the receiver).

مع (with) هذه (these) التغييرات (changes)، يُترجم (compiles) الكود (the code)! نحن (we're) هناك (getting there)!

#### تطبيق طريقة `execute` (Implementing the `execute` Method)

لننفّذ (let's implement) أخيرًا (finally) طريقة (the method) `execute` على (on) `ThreadPool`. سنغيّر (we'll also change) أيضًا (also) `Job` من بنية (from a struct) إلى اسم (to a) مستعار (type alias) للنوع (type) لكائن (for a trait object) سمة (trait) يحمل (that holds) نوع (the type of) الإغلاق (the closure) الذي (that) يتلقّاه (receives) `execute`. كما (as) تمت مناقشته (was discussed) في قسم (in the section) ["Type Synonyms and Type
Aliases"][type-aliases]<!-- ignore --> في الفصل (in Chapter) 20، تسمح (allow) لنا (us) أسماء (type aliases) الأنواع المستعارة (type) بجعل (to make) الأنواع (types) الطويلة (long) أقصر (shorter) من أجل (for) سهولة (ease of) الاستخدام (use). انظر (look) إلى القائمة (at Listing) 21-19.

<Listing number="21-19" file-name="src/lib.rs" caption="إنشاء اسم مستعار `Job` للنوع لـ `Box` يحمل كل إغلاق ثم إرسال الوظيفة أسفل القناة (Creating a `Job` type alias for a `Box` that holds each closure and then sending the job down the channel)">

```rust,noplayground
{{#rustdoc_include ../listings/ch21-web-server/listing-21-19/src/lib.rs:here}}
```

</Listing>

بعد (after) إنشاء (creating) نسخة (instance) `Job` جديدة (a new) باستخدام (using) الإغلاق (the closure) الذي (that) نحصل (we get) عليه (get) في (in) `execute`، نُرسل (we send) تلك (that) الوظيفة (job) أسفل (down) نهاية (the end) الإرسال (sending) من القناة (of the channel). نستدعي (we're calling) `unwrap` على (on) `send` لحالة (for the case) فشل (the sending fails) الإرسال (sending). قد (might) يحدث (happen) هذا (this) إذا (if)، على سبيل المثال (for example)، أوقفنا (we stop) جميع (all) خيوطنا (our threads) من التنفيذ (from executing)، مما (meaning) يعني (meaning) أن النهاية (that the) المُستقبِلة (receiving end) توقّفت (has stopped) عن استقبال (receiving) رسائل (messages) جديدة (new). في الوقت (at the moment) الحالي (current)، لا يمكننا (we can't) إيقاف (stop) خيوطنا (our threads) من التنفيذ (from executing): تستمر (continue) خيوطنا (our threads) في التنفيذ (executing) طالما (as long as) يوجد (exists) المجمع (the pool). السبب (the reason) الذي (that) نستخدم (we use) فيه (in) `unwrap` هو (is) أننا (that we) نعلم (know) أن حالة (that the case of) الفشل (failure) لن تحدث (won't happen)، لكن (but) المصرِّف (the compiler) لا يعرف (doesn't know) ذلك (that).

لكن (but) لسنا (we're not) بعد (quite done yet)! في (in) `Worker`، إغلاقنا (our closure) المُمرّر (being passed) إلى (to) `thread::spawn` ما زال (still) فقط (only) يشير (_references_) إلى النهاية (the) المُستقبِلة (receiving end) من القناة (of the channel). بدلاً (instead)، نحتاج (we need) الإغلاق (the closure) ليُكرّر (to loop) للأبد (forever)، يسأل (asking) النهاية (the) المُستقبِلة (receiving end) من القناة (of the channel) عن وظيفة (for a job) ويُشغّل (and running) الوظيفة (the job) عندما (when) يحصل (it gets) على واحدة (one). لنعمل (let's make) التغيير (the change) الموضّح (shown) في القائمة (in Listing) 21-20 إلى (to) `Worker::new`.

<Listing number="21-20" file-name="src/lib.rs" caption="استقبال وتنفيذ الوظائف في خيط نسخة `Worker` (Receiving and executing the jobs in the `Worker` instance's thread)">

```rust,noplayground
{{#rustdoc_include ../listings/ch21-web-server/listing-21-20/src/lib.rs:here}}
```

</Listing>

هنا (here)، نستدعي (we call) أولاً (first) `lock` على (on) `receiver` للحصول (to acquire) على القفل (the mutex)، ثم (and then) نستدعي (we call) `unwrap` للذعر (to panic) على (on) أي (any) أخطاء (errors). قد (might) يفشل (fail) الحصول (acquiring) على القفل (a lock) إذا (if) كان (is) المقفل (the mutex) في حالة (in a) مُسمّمة (_poisoned_ state)، والتي (which) يمكن (can) أن تحدث (happen) إذا (if) أصاب (panicked) خيط (some other thread) آخر (some other) بالذعر (panicked) أثناء (while) حمل (holding) القفل (the lock) بدلاً (rather than) من إطلاق (releasing) القفل (the lock). في هذه (in this) الحالة (situation)، فإن استدعاء (calling) `unwrap` لجعل (to have) هذا (this) الخيط (thread) يصاب (panic) بالذعر (panic) هو (is) الإجراء (the action) الصحيح (correct) ليُتّخذ (to take). لا تتردد (feel free) في تغيير (to change) هذا (this) `unwrap` إلى (to) `expect` مع (with) رسالة (message) خطأ (error) ذات معنى (meaningful) لك (to you).

إذا (if) حصلنا (we got) على القفل (the lock) على المقفل (on the mutex)، نستدعي (we call) `recv` لاستقبال (to receive) `Job` من القناة (from the channel). يتحرّك (moves) `unwrap` نهائي (a final) عبر (past) أي (any) أخطاء (errors) هنا (here) أيضًا (as well)، والتي (which) قد (might) تحدث (occur) إذا (if) أوقف (shut down) الخيط (the thread) الذي (holding) يحمل (holding) المُرسِل (the sender)، مشابهًا (similar) لكيفية (to how) إرجاع (returns) طريقة (the method) `send` `Err` إذا (if) أوقف (shuts down) المُستقبِل (the receiver).

يحجب (blocks) استدعاء (the call to) `recv`، لذا (so) إذا (if) لم يكن (there is) هناك (there) وظيفة (a job) بعد (yet)، فسينتظر (will wait) الخيط (the thread) الحالي (current) حتى (until) تصبح (becomes) وظيفة (a job) متاحة (available). يضمن (ensures) `Mutex<T>` أن (that) خيط (thread) `Worker` واحدًا (only one) فقط (only) في كل (at a) مرة (time) يحاول (is trying) طلب (to request) وظيفة (a job).

مجمع خيوطنا (our thread pool) الآن (is now) في حالة (in a) عمل (working state)! أعطه (give it) `cargo run` واعمل (and make) بعض (some) الطلبات (requests):

<!-- manual-regeneration
cd listings/ch21-web-server/listing-21-20
cargo run
make some requests to 127.0.0.1:7878
Can't automate because the output depends on making requests
-->

```console
$ cargo run
   Compiling hello v0.1.0 (file:///projects/hello)
warning: field `workers` is never read
 --> src/lib.rs:7:5
  |
6 | pub struct ThreadPool {
  |            ---------- field in this struct
7 |     workers: Vec<Worker>,
  |     ^^^^^^^
  |
  = note: `#[warn(dead_code)]` on by default

warning: fields `id` and `thread` are never read
  --> src/lib.rs:48:5
   |
47 | struct Worker {
   |        ------ fields in this struct
48 |     id: usize,
   |     ^^
49 |     thread: thread::JoinHandle<()>,
   |     ^^^^^^

warning: `hello` (lib) generated 2 warnings
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 4.91s
     Running `target/debug/hello`
Worker 0 got a job; executing.
Worker 2 got a job; executing.
Worker 1 got a job; executing.
Worker 3 got a job; executing.
Worker 0 got a job; executing.
Worker 2 got a job; executing.
Worker 1 got a job; executing.
Worker 3 got a job; executing.
Worker 0 got a job; executing.
Worker 2 got a job; executing.
```

نجاح (success)! الآن (now) لدينا (we have) مجمع خيوط (a thread pool) ينفّذ (that executes) الاتصالات (connections) بشكل غير متزامن (asynchronously). لا يتم (are never) أبدًا (never) إنشاء (created) أكثر (more) من أربعة (than four) خيوط (threads)، لذا (so) لن يحصل (won't get) نظامنا (our system) على حمل (overloaded) زائد (overloaded) إذا (if) تلقّى (receives) الخادوم (the server) الكثير (a lot) من الطلبات (of requests). إذا (if) قدّمنا (we make) طلبًا (a request) إلى (to) _/sleep_، فسيتمكّن (will be able) الخادوم (the server) من خدمة (to serve) طلبات (requests) أخرى (other) عن طريق (by) جعل (having) خيط (thread) آخر (another) يُشغّلها (run them).

> ملاحظة (note): إذا (if) فتحت (you open) _/sleep_ في نوافذ (in) متصفح (browser windows) متعددة (multiple) في وقت واحد (simultaneously)، فقد (they might) يُحمّلون (load) واحدًا (one) تلو الآخر (at a time) في فترات (in intervals) من خمس (of five) ثوانٍ (seconds). تُنفّذ (execute) بعض (some) متصفحات (browsers) الويب (web) نسخًا (instances) متعددة (multiple) من نفس (of the same) الطلب (request) بشكل تسلسلي (sequentially) لأسباب (for reasons) التخزين المؤقت (caching). هذا (this) القيد (limitation) ليس (is not) تسببه (caused by) خادوم الويب (our web server) الخاص بنا (our).

هذا (this) وقت (is a time) جيد (good) للتوقّف (to pause) والنظر (and consider) في كيف (how) سيكون (would be) الكود (the code) في القوائم (in Listings) 21-18، 21-19، و (and) 21-20 مختلفًا (different) إذا (if) كنا (we were) نستخدم (using) مستقبلات (futures) بدلاً (instead) من إغلاق (of a closure) للعمل (for the work) المُراد (to be) ليُنجز (done). ما (what) الأنواع (types) التي (that) ستتغيّر (would change)؟ كيف (how) سيكون (would) توقيعات (the signatures of) الطرق (the methods) مختلفة (be different)، إن (if) كانت (at all)؟ ما (what) أجزاء (parts of) الكود (the code) التي (that) ستبقى (would stay) نفسها (the same)؟

بعد (after) التعلّم (learning) عن حلقة (about the) `while let` (loop) في الفصل (in Chapter) 17 والفصل (and Chapter) 19، قد (you might) تتساءل (be wondering) لماذا (why) لم نكتب (we didn't write) كود (the code for) خيط (the thread) `Worker` كما (as) موضح (shown) في القائمة (in Listing) 21-21.

<Listing number="21-21" file-name="src/lib.rs" caption="تطبيق بديل لـ `Worker::new` باستخدام `while let` (An alternative implementation of `Worker::new` using `while let`)">

```rust,ignore,not_desired_behavior
{{#rustdoc_include ../listings/ch21-web-server/listing-21-21/src/lib.rs:here}}
```

</Listing>

يُترجم (compiles) هذا (this) الكود (code) ويعمل (and runs) لكن (but) لا ينتج (doesn't result in) عنه (result in) سلوك (behavior) الخيوط (threading) المطلوب (the desired): سيتسبّب (will cause) طلب (request) بطيء (a slow) لا يزال (still) في انتظار (in) wait (wait for) الطلبات (requests) الأخرى (other) ليتم (to be) معالجتها (processed). السبب (the reason) مُخادع (is somewhat subtle) إلى حد ما (somewhat): لا تمتلك (doesn't have) بنية (the) `Mutex` (struct) طريقة (method) `unlock` عامة (a public) لأن (because) ملكية (the ownership of) القفل (the lock) مبنية (is based) على عمر (on the lifetime of) `MutexGuard<T>` ضمن (within) `LockResult<MutexGuard<T>>` الذي (that) تُرجعه (returns) طريقة (the method) `lock`. في (at) وقت (compile time) الترجمة (compile), يمكن (can) للمُدقّق (the borrow checker) فرض (then enforce) القاعدة (the rule) بأن (that) لا يمكن (cannot be) الوصول (accessed) إلى مورد (a resource) محمي (guarded) بواسطة (by) `Mutex` ما لم (unless) نحمل (we hold) القفل (the lock). ومع ذلك (however)، يمكن (can) أن ينتج (also result in) هذا (this) التطبيق (implementation) أيضًا (also) في حمل (the lock being held) القفل (lock) لمدة (for longer) أطول (longer) من المقصود (than intended) إذا (if) لم نكن (we weren't) حريصين (mindful) على عمر (of the lifetime of) `MutexGuard<T>`.

يعمل (works) الكود (the code) في القائمة (in Listing) 21-20 الذي (that) يستخدم (uses) `let job =
receiver.lock().unwrap().recv().unwrap();` لأنه (because) مع (with) `let`، يتم (are) إسقاط (immediately dropped) أي (any) قيم (values) مؤقتة (temporary) مُستخدمة (used) في التعبير (in the expression) على الجانب (on the) الأيمن (right-hand side) من علامة (of the) المساواة (equal sign) فور (immediately) عندما (when) ينتهي (ends) عبارة (the statement) `let`. ومع ذلك (however)، `while
let` (و (and) `if let` و (and) `match`) لا تُسقط (does not drop) القيم (the values) المؤقتة (temporary) حتى (until) نهاية (the end of) الكتلة (the block) المرتبطة (associated). في القائمة (in Listing) 21-21، يبقى (remains) القفل (the lock) محمولاً (held) لمدة (for the duration of) استدعاء (the call to) `job()`، مما (meaning) يعني (meaning) أن نسخ (that the other) `Worker` (instances) الأخرى (other) لا يمكنها (cannot) استقبال (receive) وظائف (jobs).

[type-aliases]: ch20-03-advanced-types.html#type-synonyms-and-type-aliases
[integer-types]: ch03-02-data-types.html#integer-types
[moving-out-of-closures]: ch13-01-closures.html#moving-captured-values-out-of-closures
[builder]: ../std/thread/struct.Builder.html
[builder-spawn]: ../std/thread/struct.Builder.html#method.spawn
