<!-- Old headings. Do not remove or links may break. -->

<a id="turning-our-single-threaded-server-into-a-multithreaded-server"></a>
<a id="from-single-threaded-to-multithreaded-server"></a>

## من خادوم أحادي الخيط إلى خادوم متعدد الخيوط (From a Single-Threaded to a Multithreaded Server)

الآن، سيعالج الخادوم (server) كل طلب (request) بدوره، مما يعني أنه لن يعالج اتصالاً ثانيًا حتى ينتهي معالجة الاتصال الأول. إذا تلقى الخادوم المزيد والمزيد من الطلبات (requests)، فإن هذا التنفيذ التسلسلي سيكون أقل وأقل مثاليةً. إذا تلقى الخادوم طلبًا يستغرق وقتًا طويلاً لمعالجته، فسيتعين على الطلبات اللاحقة الانتظار حتى ينتهي الطلب الطويل, حتى لو كان من الممكن معالجة الطلبات الجديدة بسرعة. سنحتاج إلى إصلاح هذا، ولكن أولاً سننظر في المشكلة أثناء العمل.

<!-- Old headings. Do not remove or links may break. -->

<a id="simulating-a-slow-request-in-the-current-server-implementation"></a>

### محاكاة طلب بطيء (Simulating a Slow Request)

سننظر في كيف يمكن لطلب (request) يتم معالجته ببطء أن يؤثر على الطلبات (requests) الأخرى المقدمة إلى تطبيق (implementation of) خادومنا (our server) الحالي. تطبق القائمة 21-10 معالجة طلب إلى _/sleep_ مع استجابة بطيئة محاكاة ستتسبب في نوم الخادوم (server) لمدة خمس ثوانٍ قبل الاستجابة.

<Listing number="21-10" file-name="src/main.rs" caption="محاكاة طلب بطيء عن طريق النوم لمدة خمس ثوانٍ (Simulating a slow request by sleeping for five seconds)">

```rust,no_run
{{#rustdoc_include ../listings/ch21-web-server/listing-21-10/src/main.rs:here}}
```

</Listing>

انتقلنا من `if` إلى `match` الآن بعد أن أصبح لدينا ثلاث حالات. نحتاج إلى مطابقة (to pattern-match) صريحة على شريحة (on a slice) من `request_line` للمطابقة (to match) مع القيم الحرفية؛ لا يقوم `match` بالإشارة المرجعية (referencing) والإلغاء المرجعية (and dereferencing) التلقائية، مثل طريقة (method) المساواة.

الذراع الأولى هي نفسها كتلة (block) `if` من القائمة 21-9. تطابق (matches) الذراع الثانية طلبًا (a request) إلى _/sleep_. عند استقبال هذا الطلب (request)، سينام الخادوم (server) لمدة خمس ثوانٍ قبل عرض صفحة HTML الناجحة. الذراع الثالثة هي نفسها كتلة `else` من القائمة 21-9.

يمكنك أن ترى كم هو بدائي خادومنا (our server): المكتبات الحقيقية ستتعامل مع التعرف على طلبات (of requests) متعددة بطريقة أقل إسهابًا بكثير!

ابدأ الخادوم (the server) باستخدام `cargo run`. ثم افتح نافذتي متصفح: واحدة لـ _http://127.0.0.1:7878_ والأخرى لـ _http://127.0.0.1:7878/sleep_. إذا أدخلت URI _/_ عدة مرات، كما كان من قبل، فسترى أنه يستجيب بسرعة. ولكن إذا أدخلت _/sleep_ ثم حمّلت _/_، فسترى أن _/_ ينتظر حتى ينام `sleep` لمدة خمس ثوانٍ كاملة قبل التحميل.

هناك تقنيات متعددة يمكننا استخدامها لتجنب تراكم الطلبات (requests) خلف طلب (request) بطيء، بما في ذلك استخدام async كما فعلنا في الفصل 17؛ التقنية التي سننفذها هي مجمع خيوط (thread pool).

### تحسين الإنتاجية باستخدام مجمع خيوط (Improving Throughput with a Thread Pool)

_مجمع خيوط_ (_thread pool_) هو مجموعة من الخيوط (of threads) المولدة (spawned) التي هي جاهزة وتنتظر معالجة مهمة. عندما يتلقى البرنامج مهمة جديدة، فإنه يعيّن أحد الخيوط (the threads) في المجمع إلى المهمة، وسيعالج هذا الخيط (thread) المهمة. ستكون الخيوط المتبقية في المجمع متاحة لمعالجة أي مهام أخرى تأتي بينما يعالج الخيط (the thread) الأول. عندما ينتهي الخيط الأول من معالجة مهمته، يتم إرجاعه إلى مجمع الخيوط (threads) الخاملة، جاهزًا لمعالجة مهمة جديدة. يتيح لك مجمع خيوط (thread pool) معالجة الاتصالات بشكل متزامن (concurrently)، مما يزيد من إنتاجية خادومك (your server).

سنحد من عدد الخيوط (threads) في المجمع إلى عدد صغير لحمايتنا من هجمات DoS؛ إذا كان برنامجنا ينشئ خيطًا (thread) جديدًا لكل طلب (request) عند وصوله، فإن شخصًا يقدم 10 ملايين طلب (requests) إلى خادومنا (to our server) يمكن أن يحدث فوضى عن طريق استنفاد جميع موارد (the resources of) خادومنا (our server) ووقف معالجة الطلبات إلى حد.

بدلاً من توليد (spawning) خيوط (threads) غير محدودة، إذن، سيكون لدينا عدد ثابت من الخيوط (of threads) في انتظار في المجمع. يتم إرسال الطلبات (requests) التي تأتي إلى المجمع للمعالجة. سيحتفظ المجمع بطابور (a queue) من الطلبات (of requests) الواردة. سيستخرج كل من الخيوط (of the threads) في المجمع طلبًا (a request) من هذا الطابور (queue)، ويعالج الطلب (the request)، ثم يطلب من الطابور (the queue for) طلبًا (request) آخر. مع هذا التصميم، يمكننا معالجة ما يصل إلى _`N`_ طلبًا بشكل متزامن (concurrently)، حيث _`N`_ هو عدد الخيوط. إذا كان كل خيط (thread) يستجيب لطلب طويل التشغيل (long-running request)، فلا يزال بإمكان الطلبات اللاحقة أن تتراكم في الطابور (in the queue)، لكننا زدنا عدد الطلبات طويلة التشغيل التي يمكننا معالجتها قبل الوصول إلى تلك النقطة.

هذه التقنية هي واحدة فقط من طرق عديدة لتحسين إنتاجية خادوم ويب (a web server). الخيارات الأخرى التي قد تستكشفها هي نموذج fork/join (fork/join model)، ونموذج async I/O أحادي الخيط (single-threaded async I/O model)، ونموذج async I/O متعدد الخيوط (multithreaded async I/O model). إذا كنت مهتمًا بهذا الموضوع، يمكنك قراءة المزيد عن الحلول الأخرى ومحاولة تنفيذها (implement them)؛ مع لغة منخفضة المستوى مثل Rust، كل هذه الخيارات ممكنة.

قبل أن نبدأ في تنفيذ (implementing) مجمع خيوط (a thread pool)، دعونا نتحدث عن ما يجب أن يبدو عليه استخدام المجمع. عندما تحاول تصميم الكود، يمكن أن تساعد كتابة واجهة العميل أولاً في توجيه تصميمك. اكتب API للكود بحيث يكون منظمًا بالطريقة التي تريد استدعاءه بها؛ ثم نفذ الوظيفة (the functionality) ضمن تلك البنية (structure) بدلاً من تنفيذ الوظيفة ثم تصميم واجهة API العامة.

مشابهًا لكيفية استخدامنا للتطوير المُوجَّه بالاختبار (test-driven development) في المشروع في الفصل 12، سنستخدم التطوير المُوجَّه بالمصرِّف (compiler-driven development) هنا. سنكتب الكود الذي يستدعي الدوال (the functions) التي نريدها، ثم سننظر في الأخطاء من المصرِّف (from the compiler) لنحدد ما يجب أن نغيره بعد ذلك للحصول على الكود ليعمل. قبل أن نفعل ذلك، سنستكشف التقنية التي لن نستخدمها (we're not going to use) كنقطة بداية.

<!-- Old headings. Do not remove or links may break. -->

<a id="code-structure-if-we-could-spawn-a-thread-for-each-request"></a>

#### توليد خيط لكل طلب (Spawning a Thread for Each Request)

أولاً، لنستكشف (let's explore) كيف قد يبدو كودنا إذا أنشأ خيطًا (thread) جديدًا لكل اتصال. كما ذُكر سابقًا، هذه ليست خطتنا النهائية بسبب (because of) المشاكل مع إمكانية توليد (spawning) عدد غير محدود من الخيوط (of threads)، لكنها نقطة بداية للحصول على خادوم (server) متعدد الخيوط (multithreaded) يعمل أولاً. ثم سنضيف مجمع الخيوط (the thread pool) كتحسين، وسيكون التباين بين الحلين أسهل.

تُظهر القائمة 21-11 التغييرات لعملها على `main` لتوليد (to spawn) خيط (thread) جديد لمعالجة كل تدفق (stream) ضمن حلقة (loop) `for`.

<Listing number="21-11" file-name="src/main.rs" caption="توليد خيط جديد لكل تدفق (Spawning a new thread for each stream)">

```rust,no_run
{{#rustdoc_include ../listings/ch21-web-server/listing-21-11/src/main.rs:here}}
```

</Listing>

كما تعلمت في الفصل 16، سينشئ `thread::spawn` خيطًا (thread) جديدًا ثم يشغّل الكود في الإغلاق (in the closure) في الخيط الجديد (new thread). إذا شغّلت هذا الكود وحمّلت _/sleep_ في متصفحك، ثم _/_ في علامتي تبويب أخريين، فستجد بالفعل أن الطلبات (that the requests) إلى _/_ لا يتعين عليها أن تنتظر حتى ينتهي _/sleep_ من. ومع ذلك، كما ذكرنا، سيُغرق هذا في النهاية النظام لأنك (because you) ستصنع خيوطًا (threads) جديدة بدون أي حد.

قد تتذكر أيضًا من الفصل 17 أن هذا بالضبط هو نوع الحالة التي تتألق فيها async و await حقًا! احتفظ بذلك في ذهنك بينما نبني مجمع الخيوط (the thread pool) وفكّر في كيف ستبدو الأشياء مختلفة أو نفسها مع async.

<!-- Old headings. Do not remove or links may break. -->

<a id="creating-a-similar-interface-for-a-finite-number-of-threads"></a>

#### إنشاء عدد محدود من الخيوط (Creating a Finite Number of Threads)

نريد أن يعمل مجمع خيوطنا (our thread pool) بطريقة مماثلة ومألوفة بحيث لا يتطلب الانتقال من الخيوط (from threads) إلى مجمع خيوط (to a thread pool) تغييرات كبيرة في الكود الذي يستخدم واجهة API الخاصة بنا. تُظهر القائمة 21-12 الواجهة الافتراضية لبنية `ThreadPool` (struct) التي نريد استخدامها بدلاً من `thread::spawn`.

<Listing number="21-12" file-name="src/main.rs" caption="واجهة `ThreadPool` المثالية الخاصة بنا (Our ideal `ThreadPool` interface)">

```rust,ignore,does_not_compile
{{#rustdoc_include ../listings/ch21-web-server/listing-21-12/src/main.rs:here}}
```

</Listing>

نستخدم `ThreadPool::new` لإنشاء مجمع خيوط (thread pool) جديد بعدد قابل للتكوين من الخيوط (of threads)، في هذه الحالة أربعة. ثم، في حلقة `for` (loop)، لدى `pool.execute` واجهة مماثلة لـ `thread::spawn` من حيث أنه يأخذ إغلاقًا (closure) يجب أن يشغّله المجمع لكل تدفق (stream). نحتاج إلى تنفيذ (to implement) `pool.execute` بحيث يأخذ الإغلاق (the closure) ويعطيه إلى خيط (to a thread) في المجمع ليشغّله. لن يُترجم هذا الكود بعد، لكن سنحاول حتى يتمكن المصرِّف (the compiler) من توجيهنا في كيفية إصلاحه.

<!-- Old headings. Do not remove or links may break. -->

<a id="building-the-threadpool-struct-using-compiler-driven-development"></a>

#### بناء `ThreadPool` باستخدام التطوير المُوجَّه بالمصرِّف (Building `ThreadPool` Using Compiler-Driven Development)

قم بعمل التغييرات في القائمة 21-12 إلى _src/main.rs_، ثم لنستخدم (let's use) أخطاء المصرِّف (compiler) من `cargo check` لقيادة تطويرنا. فيما يلي الخطأ الأول الذي نحصل عليه:

```console
{{#include ../listings/ch21-web-server/listing-21-12/output.txt}}
```

عظيم! يخبرنا هذا الخطأ أننا نحتاج إلى نوع (type) أو وحدة (or module) `ThreadPool`، لذا سنبني واحدًا الآن. سيكون تطبيق (the implementation of) `ThreadPool` الخاص بنا مستقلاً عن نوع العمل الذي يقوم به خادوم الويب (our web server) الخاص بنا. لذا، لنحوّل (let's switch) حزمة (the crate) `hello` من حزمة ثنائية (binary crate) إلى حزمة مكتبة (library crate) لحمل تطبيق `ThreadPool` الخاص بنا. بعد أن نغيّر إلى حزمة مكتبة، يمكننا أيضًا استخدام مكتبة مجمع الخيوط (thread pool library) المنفصلة لأي عمل نريد القيام به باستخدام مجمع خيوط (a thread pool)، وليس فقط لخدمة طلبات (requests) الويب.

أنشئ ملفًا _src/lib.rs_ يحتوي على الآتي، وهو أبسط تعريف لبنية `ThreadPool` (struct) يمكننا أن نمتلكه الآن:

<Listing file-name="src/lib.rs">

```rust,noplayground
{{#rustdoc_include ../listings/ch21-web-server/no-listing-01-define-threadpool-struct/src/lib.rs}}
```

</Listing>

ثم، حرّر ملف _main.rs_ لجلب `ThreadPool` إلى النطاق (into scope) من حزمة المكتبة (library crate) بإضافة الكود التالي إلى أعلى _src/main.rs_:

<Listing file-name="src/main.rs">

```rust,ignore
{{#rustdoc_include ../listings/ch21-web-server/no-listing-01-define-threadpool-struct/src/main.rs:here}}
```

</Listing>

لن يعمل هذا الكود بعد، لكن لنتحقق منه مرة أخرى للحصول على الخطأ التالي الذي نحتاج إلى معالجته (to address):

```console
{{#include ../listings/ch21-web-server/no-listing-01-define-threadpool-struct/output.txt}}
```

يشير هذا الخطأ أننا نحتاج بعد ذلك إلى إنشاء دالة (function) مرتبطة باسم `new` لـ `ThreadPool`. نعلم أيضًا أن `new` يجب أن يكون لها معامل (parameter) واحد يمكن أن يقبل `4` كوسيطة ويجب أن تُرجع نسخة من `ThreadPool`. لنطبق أبسط دالة `new` ستكون لها تلك الخصائص:

<Listing file-name="src/lib.rs">

```rust,noplayground
{{#rustdoc_include ../listings/ch21-web-server/no-listing-02-impl-threadpool-new/src/lib.rs}}
```

</Listing>

اخترنا `usize` كنوع (as the type) لمعامل (for the parameter) `size` لأننا نعلم أن عددًا سالبًا من الخيوط (of threads) لا يكون لا معنى له. نعلم أيضًا أننا سنستخدم (will use) هذا `4` كعدد من العناصر في مجموعة من الخيوط، وهو ما يُستخدم (is used) له نوع (type) `usize`، كما تمت مناقشته في قسم ["Integer Types"][integer-types]<!--
ignore --> في الفصل 3.

لنتحقق من الكود مرة أخرى:

```console
{{#include ../listings/ch21-web-server/no-listing-02-impl-threadpool-new/output.txt}}
```

الآن يحدث الخطأ لأننا ليس لدينا طريقة (method) `execute` على `ThreadPool`. تذكّر من قسم ["Creating a Finite Number of Threads"](#creating-a-finite-number-of-threads)<!-- ignore --> أننا قررنا أن مجمع خيوطنا (that our thread pool) يجب أن يكون له واجهة مماثلة لـ `thread::spawn`. بالإضافة، سننفذ دالة (the function) `execute` بحيث تأخذ الإغلاق (the closure) الذي أُعطيت وتعطيه إلى خيط خامل (thread) في المجمع ليشغّله.

سنحدّد طريقة (the method) `execute` على `ThreadPool` لتأخذ إغلاقًا (a closure) كمعامل (as a parameter). تذكّر من قسم ["Moving Captured Values Out of
Closures"][moving-out-of-closures]<!-- ignore --> في الفصل 13 أننا يمكننا أخذ إغلاقات (closures) كمعاملات (as parameters) باستخدام ثلاث سمات (traits) مختلفة: `Fn`، `FnMut`، و `FnOnce`. نحتاج إلى تحديد أي نوع من الإغلاق (of closure) نستخدمه هنا. نعلم أننا سننتهي بفعل شيء مماثل للتطبيق (to the implementation of) `thread::spawn` للمكتبة القياسية (of the standard library)، لذا يمكننا أن ننظر في ما القيود (bounds) التي تمتلكها توقيع `thread::spawn` على معامله (on its parameter). يُظهر لنا التوثيق الآتي:

```rust,ignore
pub fn spawn<F, T>(f: F) -> JoinHandle<T>
    where
        F: FnOnce() -> T,
        F: Send + 'static,
        T: Send + 'static,
```

معامل (parameter) النوع (type) `F` هو الذي نهتم به هنا؛ معامل (the parameter) النوع `T` متعلق بالقيمة المُرجعة، ولسنا مهتمين بذلك. يمكننا أن نرى أن `spawn` يستخدم `FnOnce` كقيد (as the trait bound) السمة (trait) على `F`. هذا ربما ما نريده أيضًا، لأننا (because we'll) سنمرر في النهاية الوسيطة التي نحصل عليها في `execute` إلى `spawn`. يمكننا أن نكون واثقين أكثر أن `FnOnce` هي السمة (the trait) التي نريد استخدامها لأن الخيط (the thread) لتشغيل طلب (a request) سيُنفّذ فقط إغلاق (the closure of) ذلك الطلب (request) مرة واحدة، وهو ما يطابق (matches) `Once` في `FnOnce`.

معامل النوع (type parameter) `F` لديه أيضًا قيد (bound) السمة (trait) `Send` وقيد العمر (lifetime bound) `'static`، والتي مفيدة (useful) في موقفنا: نحتاج `Send` لنقل الإغلاق (the closure) من خيط واحد (thread) إلى آخر و `'static` لأننا لا نعرف كم سيستغرق الخيط (the thread) للتنفيذ (to execute). لننشئ طريقة `execute` (method) على `ThreadPool` ستأخذ معاملاً (parameter) عامًا (generic) من نوع (of type) `F` مع هذه القيود (bounds):

<Listing file-name="src/lib.rs">

```rust,noplayground
{{#rustdoc_include ../listings/ch21-web-server/no-listing-03-define-execute/src/lib.rs:here}}
```

</Listing>

ما زلنا نستخدم `()` بعد `FnOnce` لأن هذا `FnOnce` يمثل إغلاقًا (closure) لا يأخذ معاملات (parameters) ويُرجع نوع الوحدة (unit type) `()`. مثل تعريفات الدوال (functions)، يمكن حذف نوع (the return type) الإرجاع من التوقيع، لكن حتى لو لم يكن لدينا معاملات، ما زلنا نحتاج إلى الأقواس.

مرة أخرى، هذا هو أبسط تطبيق (implementation) لطريقة (of the method) `execute`: لا تفعل شيئًا، لكن نحن فقط نحاول جعل كودنا يُترجم. لنتحقق منه مرة أخرى:

```console
{{#include ../listings/ch21-web-server/no-listing-03-define-execute/output.txt}}
```

يُترجم! ولكن لاحظ أنه إذا حاولت `cargo run` وقدّمت طلبًا (a request) في المتصفح، فسترى الأخطاء في المتصفح التي رأيناها في بداية الفصل. مكتبتنا (our library) لا تستدعي فعلاً الإغلاق (the closure) الممرر إلى `execute` بعد!

> ملاحظة: قول قد تسمعه عن اللغات ذات المصرِّفات (compilers) الصارمة، مثل Haskell و Rust، هو "If the code compiles, it works." لكن هذا القول ليس صحيحًا عالميًا. مشروعنا يُترجع، لكن لا يفعل شيئًا على الإطلاق! إذا كنا نبني مشروعًا حقيقيًا، كاملاً (complete)، فهذا سيكون وقتًا جيدًا لبدء كتابة اختبارات (tests) الوحدة لللتحقق من أن الكود يُترجع _and_ ولديه السلوك الذي نريده.

فكّر: ما سيكون مختلفًا هنا إذا كنا سنُنفّذ (going to execute) مستقبلاً بدلاً من إغلاق (of a closure)؟

#### التحقق من عدد الخيوط في `new` (Validating the Number of Threads in `new`)

نحن لا نفعل أي شيء بالمعاملات (with the parameters) لـ `new` و `execute`. لننفّذ أجسام هذه الدوال (functions) بالسلوك الذي نريده. للبدء، لنفكّر (let's think) في `new`. اخترنا سابقًا نوعًا (type) غير موقّع لمعامل (for the parameter) `size` لأن مجمعًا بعدد سالب من الخيوط (of threads) لا يكون منطقيًا. ومع ذلك، مجمع بصفر خيوط (threads) أيضًا لا يكون منطقيًا، ومع ذلك الصفر هو `usize` صالح تمامًا. سنضيف كودًا للتحقق من أن `size` أكبر من صفر قبل أن نُرجع نسخة `ThreadPool`، وسنجعل البرنامج يصاب (panic) بالذعر إذا تلقى صفرًا باستخدام ماكرو (the macro) `assert!`، كما موضح في القائمة 21-13.

<Listing number="21-13" file-name="src/lib.rs" caption="تطبيق `ThreadPool::new` للذعر إذا كان `size` صفرًا (Implementing `ThreadPool::new` to panic if `size` is zero)">

```rust,noplayground
{{#rustdoc_include ../listings/ch21-web-server/listing-21-13/src/lib.rs:here}}
```

</Listing>

أضفنا أيضًا بعض التوثيق لـ `ThreadPool` مع تعليقات التوثيق. لاحظ أننا اتبعنا ممارسات التوثيق الجيدة بإضافة قسم يستدعي المواقف التي يمكن أن تصاب (panic) فيها دالتنا (our function) بالذعر، كما تمت مناقشته في الفصل 14. حاول تشغيل `cargo doc --open` والنقر على بنية `ThreadPool` (struct) لترى ما يبدو التوثيق المُنشأ لـ `new`!

بدلاً من إضافة ماكرو (the macro) `assert!` كما فعلنا هنا، يمكننا تغيير `new` إلى `build` وإرجاع `Result` كما فعلنا مع `Config::build` في مشروع I/O في القائمة 12-9. لكن قررنا في هذه الحالة أن محاولة إنشاء مجمع خيوط (a thread pool) بدون أي خيوط (threads) يجب أن يكون خطأً غير قابل للاسترداد. إذا كنت طموحًا، حاول كتابة دالة (a function) باسم `build` مع التوقيع التالي للمقارنة مع دالة (the function) `new`:

```rust,ignore
pub fn build(size: usize) -> Result<ThreadPool, PoolCreationError> {
```

#### إنشاء مساحة لتخزين الخيوط (Creating Space to Store the Threads)

الآن بعد أن لدينا طريقة لنعرف that لدينا عددًا صالحًا من الخيوط (of threads) للتخزين في المجمع، يمكننا إنشاء تلك الخيوط (threads) وتخزينها في بنية `ThreadPool` (struct) قبل إرجاع البنية (the struct). لكن كيف نُخزّن خيطًا (a thread)؟ لنلقِ (let's take) نظرة أخرى على توقيع `thread::spawn`:

```rust,ignore
pub fn spawn<F, T>(f: F) -> JoinHandle<T>
    where
        F: FnOnce() -> T,
        F: Send + 'static,
        T: Send + 'static,
```

تُرجع دالة (the function) `spawn` `JoinHandle<T>`، حيث `T` هو النوع (the type) الذي يُرجعه الإغلاق (the closure). لنحاول استخدام `JoinHandle` أيضًا ونرى ما يحدث. في حالتنا، الإغلاقات (the closures) التي نمررها إلى مجمع الخيوط (to the thread pool) ستعالج الاتصال ولن تُرجع أي شيء، لذا `T` سيكون نوع الوحدة (unit type) `()`.

سيُترجع الكود في القائمة 21-14، لكن لا ينشئ أي خيوط (threads) بعد. غيّرنا تعريف `ThreadPool` ليحمل متجهًا (a vector) من نسخ `thread::JoinHandle<()>`، وعيّنّا المتجه (the vector) بسعة `size`، وأعددنا (and set up) حلقة `for` (loop) ستُشغّل بعض الكود لإنشاء الخيوط (the threads)، وأرجعنا نسخة `ThreadPool` تحتويها.

<Listing number="21-14" file-name="src/lib.rs" caption="إنشاء متجه لـ `ThreadPool` لحمل الخيوط (Creating a vector for `ThreadPool` to hold the threads)">

```rust,ignore,not_desired_behavior
{{#rustdoc_include ../listings/ch21-web-server/listing-21-14/src/lib.rs:here}}
```

</Listing>

جلبنا `std::thread` إلى النطاق (into scope) في حزمة المكتبة (library crate) لأننا (because we're) نستخدم `thread::JoinHandle` كنوع (as the type of) العناصر في المتجه (in the vector) في `ThreadPool`.

بمجرد استقبال حجم صالح، ينشئ `ThreadPool` الخاص بنا متجهًا (vector) جديدًا يمكن أن يحمل عناصر `size`. تؤدي دالة (the function) `with_capacity` نفس المهمة مثل `Vec::new` لكن مع فرق مهم: تُخصّص مسبقًا مساحة في المتجه (in the vector). لأننا نعلم أننا نحتاج إلى تخزين عناصر `size` في المتجه، فإن القيام بهذا التخصيص (allocation) مقدمًا أكثر كفاءة قليلاً من استخدام `Vec::new`، الذي يغيّر نفسه بينما يتم إدراج العناصر.

عندما تُشغّل `cargo check` مرة أخرى، يجب أن ينجح.

<!-- Old headings. Do not remove or links may break. -->

<a id ="a-worker-struct-responsible-for-sending-code-from-the-threadpool-to-a-thread"></a>

#### إرسال الكود من `ThreadPool` إلى خيط (Sending Code from the `ThreadPool` to a Thread)

تركنا تعليقًا في حلقة `for` (loop) في القائمة 21-14 بخصوص إنشاء الخيوط (the threads). هنا، سننظر في كيفية نُنشئ فعلاً الخيوط. توفر المكتبة القياسية (the standard library) `thread::spawn` كطريقة لإنشاء خيوط (threads)، و `thread::spawn` تتوقع أن تحصل على بعض الكود الذي يجب أن يُشغّله الخيط (the thread) بمجرد إنشاء الخيط. ومع ذلك، في حالتنا، نريد إنشاء الخيوط وجعلها تنتظر (_wait_) للكود الذي سنرسله (we'll send) لاحقًا. لا تتضمن تطبيق (the implementation of) المكتبة القياسية للخيوط (for threads) أي طريقة للقيام بذلك؛ علينا أن ننفّذه (implement it) يدويًا.

سننفّذ هذا السلوك بإدخال بنية (data structure) بيانات جديدة بين `ThreadPool` والخيوط (and the threads) التي ستدير هذا السلوك الجديد. سنسمّي بنية البيانات هذه _Worker_ (Worker)، وهو مصطلح شائع في تطبيقات (in implementations) الترجمة (pooling). يلتقط `Worker` الكود الذي يحتاج إلى التشغيل ويُشغّل الكود في خيطه (in its thread).

فكّر في الناس العاملين في المطبخ في مطعم: ينتظر العمّال (the workers) حتى تأتي الطلبات من العملاء، ثم هم مسؤولون عن أخذ تلك الطلبات وملئها.

بدلاً من تخزين متجه (a vector) من نسخ `JoinHandle<()>` في مجمع الخيوط (in the thread pool)، سنُخزّن نسخ من بنية `Worker` (struct). سيُخزّن كل `Worker` نسخة واحدة `JoinHandle<()>`. ثم، سننفّذ طريقة (a method) على `Worker` ستأخذ إغلاقًا (a closure) من الكود ليُشغّل وترسله (and send it) إلى الخيط (to the thread) الذي يعمل بالفعل للتنفيذ. سنعطي أيضًا كل `Worker` معرّفًا بحيث نتمكن من التمييز بين نسخ `Worker` المختلفة في المجمع عند التسجيل أو التصحيح (or debugging).

فيما يلي العملية الجديدة التي ستحدث عندما ننشئ `ThreadPool`. سننفّذ الكود الذي يُرسل الإغلاق (the closure) إلى الخيط (to the thread) بعد أن يكون `Worker` مُعدًّا (set up) بهذه الطريقة:

1. حدّد بنية `Worker` (struct) تحمل معرّفًا `id` و `JoinHandle<()>`.
2. غيّر `ThreadPool` ليحمل متجهًا (a vector) من نسخ `Worker`.
3. حدّد دالة (a function) `Worker::new` تأخذ رقم معرّف وتُرجع نسخة `Worker` تحمل المعرّف وخيطًا (and a thread) مُولّدًا (spawned) مع إغلاق (closure) فارغ.
4. في `ThreadPool::new`، استخدم عداد حلقة `for` (loop) لتوليد معرّف، وأنشئ `Worker` جديدًا بذلك المعرّف، وخزّن `Worker` في المتجه (in the vector).

إذا كنت لتحدٍ، حاول تطبيق (implementing) هذه التغييرات بنفسك قبل النظر في الكود في القائمة 21-15.

مستعد؟ فيما يلي القائمة 21-15 مع إحدى الطرق لعمل التعديلات (the modifications) المذكورة.

<Listing number="21-15" file-name="src/lib.rs" caption="تعديل `ThreadPool` لحمل نسخ `Worker` بدلاً من حمل الخيوط مباشرة (Modifying `ThreadPool` to hold `Worker` instances instead of holding threads directly)">

```rust,noplayground
{{#rustdoc_include ../listings/ch21-web-server/listing-21-15/src/lib.rs:here}}
```

</Listing>

غيّرنا اسم الحقل على `ThreadPool` من `threads` إلى `workers` لأنه (because it's) الآن يحمل نسخ `Worker` بدلاً من نسخ `JoinHandle<()>`. نستخدم العداد في حلقة `for` (loop) كوسيطة لـ `Worker::new`، ونُخزّن كل `Worker` جديد في المتجه (in the vector) المسمّى `workers`.

لا الكود الخارجي (مثل خادومنا (our server) في _src/main.rs_) أن يعرف تفاصيل التطبيق (the implementation) المتعلقة باستخدام بنية (struct) `Worker` ضمن `ThreadPool`، لذا نجعل بنية `Worker` ودالتها (and its function) `new` خاصة. تستخدم دالة (the function) `Worker::new` المعرّف `id` الذي نعطيه وتُخزّن نسخة `JoinHandle<()>` التي يتم إنشاؤها بتوليد (by spawning) خيط (thread) جديد باستخدام إغلاق (closure) فارغ.

> ملاحظة: إذا لم يتمكن نظام التشغيل من إنشاء خيط (a thread) لأنه ليست هناك موارد (resources) نظام كافية، فسيصاب (will panic) `thread::spawn` بالذعر (panic). هذا سيتسبب في إصابة خادومنا (our server) بالكامل بالذعر (to panic)، حتى على الرغم من أن إنشاء بعض الخيوط (threads) قد ينجح. من أجل بساطة الأمر (simplicity's sake)، هذا السلوك جيد، لكن في تطبيق مجمع خيوط (thread pool) إنتاجي (production implementation)، من المحتمل أن ترغب في استخدام
> [`std::thread::Builder`][builder]<!-- ignore --> وطريقته (and its method)
> [`spawn`][builder-spawn]<!-- ignore --> التي تُرجع `Result` بدلاً.

سيُترجم هذا الكود ويُخزّن عدد نسخ `Worker` الذي حددناه كوسيطة لـ `ThreadPool::new`. لكن ما زلنا لا نعالج (_still_ not processing) الإغلاق (the closure) الذي نحصل عليه في `execute`. لننظر في كيفية ذلك بعد ذلك.

#### إرسال الطلبات إلى الخيوط عبر القنوات (Sending Requests to Threads via Channels)

المشكلة التالية التي سنتعامل معها هي أن الإغلاقات (that the closures) المُعطاة لـ `thread::spawn` لا تفعل شيئًا على الإطلاق. حاليًا، نحصل على الإغلاق (the closure) الذي نريد تنفيذه (to execute) في طريقة (in the method) `execute`. لكن نحتاج إلى إعطاء `thread::spawn` إغلاقًا (a closure) ليُشغّله عندما ننشئ كل `Worker` أثناء إنشاء `ThreadPool`.

نريد بنيات `Worker` (structs) التي أنشأناها أن تجلب الكود ليُشغّل من طابور (from a queue) محفوظ في `ThreadPool` وترسل (and send) ذلك الكود إلى خيطه (to its thread) ليُشغّله.

القنوات (the channels) التي تعلّمناها في الفصل 16—طريقة بسيطة (a simple) للتواصل بين خيطين (between two threads) اثنين—ستكون مثالية لحالة الاستخدام (use case) هذه. سنستخدم قناة (a channel) لتعمل (to function) كطابور (as a queue) للوظائف (of jobs)، وسيُرسل (and will send) `execute` وظيفة (a job) من `ThreadPool` إلى نسخ `Worker`، التي ستُرسل الوظيفة (the job) إلى خيطها (to its thread). فيما يلي الخطة:

1. سينشئ `ThreadPool` قناة (a channel) ويحتفظ بالمُرسِل (to the sender).
2. سيحتفظ كل `Worker` بالمُستقبِل (to the receiver).
3. سننشئ بنية (struct) `Job` جديدة ستحمل الإغلاقات (the closures) التي نريد إرسالها أسفل القناة (the channel).
4. ستُرسل طريقة (the method) `execute` الوظيفة (the job) التي تريد تنفيذها (to execute) عبر المُرسِل (the sender).
5. في خيطه (in its thread)، سيُكرّر (will loop) `Worker` على مُستقبِله (over its receiver) ويُنفّذ (and execute) إغلاقات (the closures of) أي وظائف (jobs) يتلقّاها.

لنبدأ بإنشاء قناة (a channel) في `ThreadPool::new` والاحتفاظ بالمُرسِل (on to the sender) في نسخة `ThreadPool`، كما موضح في القائمة 21-16. لا تحمل بنية `Job` (struct) أي شيء الآن لكن ستكون نوع (the type of) العنصر الذي نرسله (we're sending) أسفل القناة (the channel).

<Listing number="21-16" file-name="src/lib.rs" caption="تعديل `ThreadPool` لتخزين مُرسِل قناة تُرسل نسخ `Job` (Modifying `ThreadPool` to store the sender of a channel that sends `Job` instances)">

```rust,noplayground
{{#rustdoc_include ../listings/ch21-web-server/listing-21-16/src/lib.rs:here}}
```

</Listing>

في `ThreadPool::new`، ننشئ قناتنا (our channel) الجديدة ونجعل المجمع يحتفظ بالمُرسِل (the sender). سيُترجم هذا بنجاح.

لنحاول تمرير مُستقبِل (the receiver of) القناة (the channel) إلى كل `Worker` بينما ينشئ مجمع الخيوط (the thread pool) القناة. نعلم أننا نريد استخدام المُستقبِل (the receiver) في الخيط (in the thread) الذي تولّده (spawn) نسخ `Worker`، لذا سنُشير (we'll reference) إلى معامل (to the parameter) `receiver` في الإغلاق (in the closure). لن يُترجم الكود في القائمة 21-17 تمامًا بعد.

<Listing number="21-17" file-name="src/lib.rs" caption="تمرير مُستقبِل القناة إلى العمّال (Passing the receiver of the channel to the workers)">

```rust,ignore,does_not_compile
{{#rustdoc_include ../listings/ch21-web-server/listing-21-17/src/lib.rs:here}}
```

</Listing>

أجرينا بعض التغييرات الصغيرة والمباشرة: مررنا المُستقبِل (the receiver) إلى `Worker::new`، ثم نستخدمه (we use it) داخل الإغلاق (the closure).

عندما نحاول فحص هذا الكود، نحصل على هذا الخطأ:

```console
{{#include ../listings/ch21-web-server/listing-21-17/output.txt}}
```

يحاول الكود تمرير `receiver` إلى نسخ `Worker` متعددة. لن يعمل هذا، كما ستتذكّر من الفصل 16: تطبيق (the implementation of) القناة (the channel) الذي توفّره Rust هو مُنتِج (_producer_) متعدد، مُستهلِك (_consumer_) واحد. هذا يعني أننا لا يمكن فقط استنساخ النهاية الاستهلاكية من القناة (of the channel) لإصلاح هذا الكود. نحن أيضًا لا نريد إرسال رسالة عدة مرات إلى مُستهلكين متعددين؛ نريد قائمة واحدة من الرسائل مع نسخ `Worker` متعددة بحيث تتم تُعالج كل رسالة مرة واحدة.

بالإضافة، فإن أخذ وظيفة (a job) من طابور (from the queue of) القناة (the channel) يتضمن تعديل (mutating) `receiver`، لذا تحتاج الخيوط (the threads) إلى طريقة آمنة لمشاركة وتعديل (and modify) `receiver`؛ وإلا، قد نحصل على شروط سباق (كما تمت تغطيته في الفصل 16).

تذكّر المؤشرات (the pointers) الذكية الآمنة للخيط (thread) التي تمت مناقشتها في الفصل 16: لمشاركة الملكية (ownership) عبر خيوط (threads) متعددة والسماح للخيوط (the threads) بتعديل (to mutate) القيمة، نحتاج إلى استخدام `Arc<Mutex<T>>`. سيسمح (will let) النوع (the type) `Arc` لنسخ `Worker` متعددة بامتلاك المُستقبِل (the receiver)، وسيضمن `Mutex` أن `Worker` واحدًا فقط يحصل على وظيفة (a job) من المُستقبِل (from the receiver) في كل مرة. تُظهر القائمة 21-18 التغييرات التي نحتاج إلى عملها.

<Listing number="21-18" file-name="src/lib.rs" caption="مشاركة المُستقبِل بين نسخ `Worker` باستخدام `Arc` و `Mutex` (Sharing the receiver among the `Worker` instances using `Arc` and `Mutex`)">

```rust,noplayground
{{#rustdoc_include ../listings/ch21-web-server/listing-21-18/src/lib.rs:here}}
```

</Listing>

في `ThreadPool::new`، نضع المُستقبِل (the receiver) في `Arc` و `Mutex`. لكل `Worker` جديد، نستنسخ `Arc` لزيادة عداد المراجع (the reference) بحيث تتمكن نسخ `Worker` من مشاركة ملكية (ownership of) المُستقبِل.

مع هذه التغييرات، يُترجم الكود! نحن هناك!

#### تطبيق طريقة `execute` (Implementing the `execute` Method)

لننفّذ أخيرًا طريقة (the method) `execute` على `ThreadPool`. سنغيّر أيضًا `Job` من بنية (from a struct) إلى اسم مستعار (type alias) للنوع (type) لكائن (for a trait object) سمة (trait) يحمل نوع (the type of) الإغلاق (the closure) الذي يتلقّاه `execute`. كما تمت مناقشته في قسم ["Type Synonyms and Type
Aliases"][type-aliases]<!-- ignore --> في الفصل 20، تسمح لنا أسماء (type aliases) الأنواع المستعارة بجعل الأنواع (types) الطويلة أقصر من أجل سهولة الاستخدام. انظر إلى القائمة 21-19.

<Listing number="21-19" file-name="src/lib.rs" caption="إنشاء اسم مستعار `Job` للنوع لـ `Box` يحمل كل إغلاق ثم إرسال الوظيفة أسفل القناة (Creating a `Job` type alias for a `Box` that holds each closure and then sending the job down the channel)">

```rust,noplayground
{{#rustdoc_include ../listings/ch21-web-server/listing-21-19/src/lib.rs:here}}
```

</Listing>

بعد إنشاء نسخة `Job` جديدة باستخدام الإغلاق (the closure) الذي نحصل عليه في `execute`، نُرسل (we send) تلك الوظيفة (job) أسفل نهاية الإرسال (sending) من القناة (of the channel). نستدعي `unwrap` على `send` لحالة فشل (the sending fails) الإرسال. قد يحدث هذا إذا، على سبيل المثال، أوقفنا جميع خيوطنا (our threads) من التنفيذ، مما يعني أن النهاية المُستقبِلة توقّفت عن استقبال رسائل جديدة. في الوقت الحالي، لا يمكننا إيقاف خيوطنا من التنفيذ: تستمر خيوطنا في التنفيذ طالما يوجد المجمع. السبب الذي نستخدم فيه `unwrap` هو أننا نعلم أن حالة الفشل لن تحدث، لكن المصرِّف (the compiler) لا يعرف ذلك.

لكن لسنا بعد! في `Worker`، إغلاقنا (our closure) المُمرّر إلى `thread::spawn` ما زال فقط يشير (_references_) إلى النهاية المُستقبِلة من القناة (of the channel). بدلاً، نحتاج الإغلاق (the closure) ليُكرّر (to loop) للأبد، يسأل النهاية المُستقبِلة من القناة عن وظيفة (for a job) ويُشغّل الوظيفة (the job) عندما يحصل على واحدة. لنعمل (let's make) التغيير الموضّح في القائمة 21-20 إلى `Worker::new`.

<Listing number="21-20" file-name="src/lib.rs" caption="استقبال وتنفيذ الوظائف في خيط نسخة `Worker` (Receiving and executing the jobs in the `Worker` instance's thread)">

```rust,noplayground
{{#rustdoc_include ../listings/ch21-web-server/listing-21-20/src/lib.rs:here}}
```

</Listing>

هنا، نستدعي أولاً `lock` على `receiver` للحصول على القفل (the mutex)، ثم نستدعي `unwrap` للذعر (to panic) على أي أخطاء. قد يفشل الحصول على القفل (a lock) إذا كان المقفل في حالة مُسمّمة (_poisoned_ state)، والتي يمكن أن تحدث إذا أصاب (panicked) خيط (some other thread) آخر بالذعر أثناء حمل القفل (the lock) بدلاً من إطلاق القفل. في هذه الحالة، فإن استدعاء `unwrap` لجعل هذا الخيط (thread) يصاب (panic) بالذعر هو الإجراء الصحيح ليُتّخذ. لا تتردد في تغيير هذا `unwrap` إلى `expect` مع رسالة خطأ ذات معنى لك.

إذا حصلنا على القفل (the lock) على المقفل (on the mutex)، نستدعي `recv` لاستقبال `Job` من القناة (from the channel). يتحرّك `unwrap` نهائي عبر أي أخطاء هنا أيضًا، والتي قد تحدث إذا أوقف الخيط (the thread) الذي يحمل المُرسِل (the sender)، مشابهًا لكيفية إرجاع طريقة (the method) `send` `Err` إذا أوقف المُستقبِل (the receiver).

يحجب (blocks) استدعاء `recv`، لذا إذا لم يكن هناك وظيفة (a job) بعد، فسينتظر الخيط (the thread) الحالي حتى تصبح وظيفة متاحة. يضمن `Mutex<T>` أن خيط (thread) `Worker` واحدًا فقط في كل مرة يحاول طلب (to request) وظيفة.

مجمع خيوطنا (our thread pool) الآن في حالة عمل! أعطه `cargo run` واعمل بعض الطلبات (requests):

<!-- manual-regeneration
cd listings/ch21-web-server/listing-21-20
cargo run
make some requests to 127.0.0.1:7878
Can't automate because the output depends on making requests
-->

```console
$ cargo run
   Compiling hello v0.1.0
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

warning: `hello` generated 2 warnings
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

نجاح! الآن لدينا مجمع خيوط (a thread pool) ينفّذ (that executes) الاتصالات بشكل غير متزامن (asynchronously). لا يتم أبدًا إنشاء أكثر من أربعة خيوط (threads)، لذا لن يحصل نظامنا على حمل زائد إذا تلقّى الخادوم (the server) الكثير من الطلبات (of requests). إذا قدّمنا طلبًا (a request) إلى _/sleep_، فسيتمكّن الخادوم من خدمة طلبات (requests) أخرى عن طريق جعل خيط (thread) آخر يُشغّلها.

> ملاحظة: إذا فتحت _/sleep_ في نوافذ متصفح متعددة في وقت واحد، فقد يُحمّلون واحدًا تلو الآخر في فترات من خمس ثوانٍ. تُنفّذ (execute) بعض متصفحات الويب نسخًا متعددة من نفس الطلب (request) بشكل تسلسلي لأسباب التخزين المؤقت. هذا القيد ليس تسببه (caused by) خادوم الويب (our web server) الخاص بنا.

هذا وقت جيد للتوقّف (to pause) والنظر في كيف سيكون الكود في القوائم 21-18، 21-19، و 21-20 مختلفًا إذا كنا نستخدم مستقبلات بدلاً من إغلاق (of a closure) للعمل المُراد ليُنجز. ما الأنواع (types) التي ستتغيّر؟ كيف سيكون توقيعات الطرق (the methods) مختلفة، إن كانت؟ ما أجزاء الكود التي ستبقى نفسها؟

بعد التعلّم عن حلقة `while let` (loop) في الفصل 17 والفصل 19، قد تتساءل لماذا لم نكتب كود خيط (the thread) `Worker` كما موضح في القائمة 21-21.

<Listing number="21-21" file-name="src/lib.rs" caption="تطبيق بديل لـ `Worker::new` باستخدام `while let` (An alternative implementation of `Worker::new` using `while let`)">

```rust,ignore,not_desired_behavior
{{#rustdoc_include ../listings/ch21-web-server/listing-21-21/src/lib.rs:here}}
```

</Listing>

يُترجم هذا الكود ويعمل لكن لا ينتج عنه سلوك الخيوط (threading) المطلوب: سيتسبّب طلب (request) بطيء لا يزال في انتظار wait الطلبات (requests) الأخرى ليتم معالجتها. السبب مُخادع إلى حد ما: لا تمتلك بنية `Mutex` (struct) طريقة (method) `unlock` عامة (a public) لأن ملكية (the ownership of) القفل (the lock) مبنية على عمر (on the lifetime of) `MutexGuard<T>` ضمن `LockResult<MutexGuard<T>>` الذي تُرجعه طريقة (the method) `lock`. في وقت الترجمة, يمكن للمُدقّق (the borrow checker) فرض (then enforce) القاعدة بأن لا يمكن الوصول إلى مورد (a resource) محمي (guarded) بواسطة `Mutex` ما لم نحمل القفل. ومع ذلك، يمكن أن ينتج هذا التطبيق (implementation) أيضًا في حمل (the lock being held) القفل (lock) لمدة أطول من المقصود إذا لم نكن حريصين على عمر (of the lifetime of) `MutexGuard<T>`.

يعمل الكود في القائمة 21-20 الذي يستخدم `let job =
receiver.lock().unwrap().recv().unwrap();` لأنه مع `let`، يتم إسقاط أي قيم مؤقتة مُستخدمة في التعبير على الجانب الأيمن من علامة المساواة فور عندما ينتهي عبارة `let`. ومع ذلك، `while
let` `if let` و `match`) لا تُسقط القيم المؤقتة حتى نهاية الكتلة (the block) المرتبطة. في القائمة 21-21، يبقى القفل (the lock) محمولاً لمدة استدعاء `job()`، مما يعني أن نسخ `Worker` الأخرى لا يمكنها استقبال وظائف (jobs).

[type-aliases]: ch20-03-advanced-types.html#type-synonyms-and-type-aliases
[integer-types]: ch03-02-data-types.html#integer-types
[moving-out-of-closures]: ch13-01-closures.html#moving-captured-values-out-of-closures
[builder]: ../std/thread/struct.Builder.html
[builder-spawn]: ../std/thread/struct.Builder.html#method.spawn
