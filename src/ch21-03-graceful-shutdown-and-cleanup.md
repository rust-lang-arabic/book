## الإيقاف الرشيق والتنظيف (Graceful Shutdown and Cleanup)

الكود (code) في القائمة (Listing) 21-20 يستجيب للطلبات (requests) بشكل غير متزامن (asynchronously) من خلال استخدام مجمع خيوط (thread pool)، كما قصدنا. نحصل على بعض التحذيرات حول الحقول (fields) `workers`، `id`، و `thread` التي لا نستخدمها بطريقة مباشرة، مما يذكّرنا بأننا لا ننظّف أي شيء. عندما نستخدم الطريقة الأقل أناقة <kbd>ctrl</kbd>-<kbd>C</kbd> لإيقاف الخيط الرئيسي (main thread)، تُوقف جميع الخيوط (threads) الأخرى فورًا أيضًا، حتى لو كانت في منتصف خدمة طلب (request).

بعد ذلك، إذن، سننفّذ سمة (trait) `Drop` لاستدعاء `join` على كل من الخيوط (threads) في المجمع (pool) حتى يتمكنوا من إنهاء الطلبات (requests) التي يعملون عليها قبل الإغلاق. ثم، سننفّذ طريقة لإخبار الخيوط (threads) بأنها يجب أن تتوقّف عن قبول طلبات (requests) جديدة وتُوقف. لرؤية هذا الكود (code) أثناء العمل، سنعدّل خادومنا (server) ليقبل طلبين فقط قبل الإيقاف الرشيق (graceful shutdown) لمجمع خيوطه (thread pool).

شيء واحد يجب ملاحظته بينما نذهب: لا يؤثّر أي من أجزاء الكود (code) التي تتعامل مع تنفيذ الإغلاقات (closures)، لذا كل شيء هنا سيكون نفسه إذا كنا نستخدم مجمع خيوط (thread pool) لوقت تشغيل (async runtime) غير متزامن (async).

### تطبيق سمة `Drop` على `ThreadPool` (Implementing the `Drop` Trait on `ThreadPool`)

لنبدأ بتطبيق `Drop` على مجمع خيوطنا (thread pool). عندما يتم إسقاط (drop) المجمع (pool)، يجب على جميع خيوطنا (threads) أن تنضم (join) للتأكّد من أنها تنهي عملها. تُظهر القائمة (Listing) 21-22 محاولة أولى على تطبيق `Drop`؛ لن يعمل هذا الكود (code) تمامًا بعد.

<Listing number="21-22" file-name="src/lib.rs" caption="الانضمام لكل خيط (thread) عندما يخرج مجمع الخيوط (thread pool) من النطاق (scope)">

```rust,ignore,does_not_compile
{{#rustdoc_include ../listings/ch21-web-server/listing-21-22/src/lib.rs:here}}
```

</Listing>

أولاً، نكرّر عبر كل من `workers` مجمع الخيوط (thread pool). نستخدم `&mut` لهذا لأن `self` هو مرجع (reference) قابل للتعديل (mutable)، ونحتاج أيضًا إلى أن نتمكّن من تعديل `worker`. لكل `worker`، نطبع رسالة تقول أن هذه نسخة (instance) `Worker` المحددة تُوقف، ثم نستدعي `join` على خيط (thread) تلك نسخة (instance) `Worker`. إذا فشل استدعاء `join`، نستخدم `unwrap` لجعل Rust تصاب بالذعر (panic) وتذهب في إيقاف غير رشيق (ungraceful shutdown).

فيما يلي الخطأ الذي نحصل عليه عندما نُترجم (compile) هذا الكود (code):

```console
{{#include ../listings/ch21-web-server/listing-21-22/output.txt}}
```

يخبرنا الخطأ أننا لا يمكننا استدعاء `join` لأننا فقط لدينا استعارة (borrow) قابلة للتعديل (mutable) من كل `worker` و`join` يأخذ ملكية (ownership) وسيطته (argument). لحلّ هذه المشكلة، نحتاج إلى نقل الخيط (thread) خارج نسخة (instance) `Worker` التي تمتلك `thread` بحيث يتمكّن `join` من استهلاك الخيط (thread). إحدى الطرق للقيام بذلك هي أخذ نفس النهج الذي اتخذناه في القائمة (Listing) 18-15. إذا كان `Worker` يحمل `Option<thread::JoinHandle<()>>`، يمكننا استدعاء طريقة (method) `take` على `Option` لنقل القيمة خارج المتغيّر (variant) `Some` وترك متغيّر (variant) `None` في مكانه. بعبارة أخرى، `Worker` الذي يعمل سيكون لديه متغيّر (variant) `Some` في `thread`، وعندما أردنا تنظيف `Worker`، سنستبدل `Some` بـ `None` بحيث لن يكون لدى `Worker` خيط (thread) ليشغّله.

ومع ذلك، الوقت الوحيد الذي سيأتي هذا سيكون عندما إسقاط (drop) `Worker`. في المقابل، سنضطر إلى التعامل مع `Option<thread::JoinHandle<()>>` في أي مكان وصلنا إلى `worker.thread`. Rust الاصطلاحية (Idiomatic Rust) تستخدم `Option` قليلاً، لكن عندما تجد نفسك تُلفّ شيئًا تعلم أنه سيكون موجودًا دائمًا في `Option` كحلّ بديل مثل هذا، فهي فكرة جيدة للبحث عن مناهج بديلة لجعل كودك (code) أنظف وأقل عرضة للأخطاء.

في هذه الحالة، يوجد بديل أفضل: طريقة (method) `Vec::drain`. تقبل معامل (parameter) نطاق (range) لتحديد أي عناصر لإزالتها من المتجه (vector) وتُرجع مُكرِّرًا (iterator) من تلك العناصر. سيؤدي تمرير بناء `..` range إلى إزالة _كل_ قيمة من المتجه (vector).

لذا، نحتاج إلى تحديث تطبيق `drop` لـ `ThreadPool` مثل هذا:

<Listing file-name="src/lib.rs">

```rust
{{#rustdoc_include ../listings/ch21-web-server/no-listing-04-update-drop-definition/src/lib.rs:here}}
```

</Listing>

يحلّ هذا خطأ المصرِّف (compiler) ولا يتطلّب أي تغييرات أخرى على كودنا (code). لاحظ أنه، لأن يمكن استدعاء drop عند الذعر (panicking)، يمكن أن يصاب unwrap أيضًا بالذعر (panic) ويتسبّب في ذعر مزدوج (double panic)، مما الذي يُعطّل البرنامج (program) فورًا وينهي أي تنظيف جارٍ. هذا جيد لبرنامج مثال، لكن ليس لا يُنصح به لكود (code) إنتاجي (production).

### الإشارة للخيوط (Threads) للتوقف عن الاستماع للوظائف (Jobs)

مع جميع التغييرات التي أجريناها، يُترجم (compile) كودنا (code) بدون أي تحذيرات. ومع ذلك، الأخبار السيئة هي أن هذا الكود (code) لا يعمل بالطريقة التي نريدها بعد. المفتاح هو المنطق في الإغلاقات (closures) التي يُشغّلها الخيوط (threads) من نسخ (instances) `Worker`: في الوقت الحالي، نستدعي `join`، لكن ذلك لن يُوقف الخيوط (threads)، لأنها تُكرّر `loop` للأبد بحثًا عن وظائف (jobs). إذا حاولنا إسقاط (drop) `ThreadPool` الخاص بنا مع تطبيقنا الحالي لـ `drop`، فسيُحجَب (block) الخيط الرئيسي (main thread) للأبد، منتظرًا للخيط (thread) الأول لينتهي.

لإصلاح هذه المشكلة، سنحتاج إلى تغيير في تطبيق `drop` لـ `ThreadPool` ثم تغيير في حلقة (loop) `Worker`.

أولاً، سنغيّر تطبيق `drop` لـ `ThreadPool` لإسقاط (drop) `sender` صراحةً قبل الانتظار للخيوط (threads) لتنتهي. تُظهر القائمة (Listing) 21-23 التغييرات على `ThreadPool` لإسقاط (drop) `sender` صراحةً. على عكس مع الخيط (thread)، هنا نحتاج فعلاً إلى استخدام `Option` لنتمكّن من نقل `sender` خارج `ThreadPool` مع `Option::take`.

<Listing number="21-23" file-name="src/lib.rs" caption="إسقاط (drop) `sender` صراحةً قبل الانضمام (join) لخيوط (threads) `Worker`">

```rust,noplayground,not_desired_behavior
{{#rustdoc_include ../listings/ch21-web-server/listing-21-23/src/lib.rs:here}}
```

</Listing>

يُغلق إسقاط (dropping) `sender` القناة (channel)، مما يُشير إلى أنه لن يتم إرسال المزيد من الرسائل. عندما يحدث ذلك، ستُرجع جميع الاستدعاءات لـ `recv` التي تقوم بها نسخ (instances) `Worker` في الحلقة اللانهائية (infinite loop) خطأً. في القائمة (Listing) 21-24، نُغيّر حلقة (loop) `Worker` للخروج من الحلقة (loop) بشكل رشيق (gracefully) في تلك الحالة، مما يعني أن الخيوط (threads) ستنتهي عندما يستدعي تطبيق `drop` لـ `ThreadPool` `join` عليها.

<Listing number="21-24" file-name="src/lib.rs" caption="الخروج صراحةً من الحلقة (loop) عندما تُرجع `recv` خطأً">

```rust,noplayground
{{#rustdoc_include ../listings/ch21-web-server/listing-21-24/src/lib.rs:here}}
```

</Listing>

لرؤية هذا الكود (code) أثناء العمل، لنعدّل `main` ليقبل طلبين فقط قبل إيقاف الخادوم (server) بشكل رشيق (gracefully)، كما موضح في القائمة (Listing) 21-25.

<Listing number="21-25" file-name="src/main.rs" caption="إيقاف الخادوم (server) بعد خدمة طلبين عن طريق الخروج من الحلقة (loop)">

```rust,ignore
{{#rustdoc_include ../listings/ch21-web-server/listing-21-25/src/main.rs:here}}
```

</Listing>

لن تريد أن خادوم ويب (web server) حقيقي يُوقف بعد خدمة طلبين فقط. هذا الكود (code) فقط يوضّح أن الإيقاف الرشيق (graceful shutdown) والتنظيف في حالة عمل جيدة.

طريقة (method) `take` محددة في سمة (trait) `Iterator` وتحدّ التكرار (iteration) لأول العنصرين اثنين الأولين. سيخرج `ThreadPool` من النطاق (scope) في نهاية `main`، وسيُشغَّل تطبيق `drop`.

ابدأ الخادوم (server) مع `cargo run` واعمل ثلاثة طلبات (requests). يجب على الطلب (request) الثالث أن يُخطئ، وفي طرفيتك (terminal)، يجب أن ترى إخراجًا مشابهًا لهذا:

<!-- manual-regeneration
cd listings/ch21-web-server/listing-21-25
cargo run
curl http://127.0.0.1:7878
curl http://127.0.0.1:7878
curl http://127.0.0.1:7878
third request will error because server will have shut down
copy output below
Can't automate because the output depends on making requests
-->

```console
$ cargo run
   Compiling hello v0.1.0 (file:///projects/hello)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.41s
     Running `target/debug/hello`
Worker 0 got a job; executing.
Shutting down.
Shutting down worker 0
Worker 3 got a job; executing.
Worker 1 disconnected; shutting down.
Worker 2 disconnected; shutting down.
Worker 3 disconnected; shutting down.
Worker 0 disconnected; shutting down.
Shutting down worker 1
Shutting down worker 2
Shutting down worker 3
```

قد ترى ترتيبًا مختلفًا من معرّفات (IDs) `Worker` والرسائل المطبوعة. يمكننا أن نرى كيفية عمل هذا الكود (code) من الرسائل: حصل النسخ (instances) `Worker` 0 و 3 على أول طلبين اثنين. توقّف الخادوم (server) عن قبول الاتصالات بعد الاتصال الثاني، وبدأ تطبيق `Drop` على `ThreadPool` في التنفيذ قبل أن يبدأ `Worker 3` حتى وظيفته (job). يقطع الاتصال إسقاط (Dropping) `sender` جميع نسخ (instances) `Worker` ويخبرها لتُوقف. تطبع نسخ (instances) `Worker` كل رسالة عندما تقطع الاتصال، ثم يستدعي مجمع الخيوط (thread pool) `join` لانتظار كل خيط (thread) `Worker` لينتهي.

لاحظ جانبًا واحدًا مثيرًا للاهتمام من هذا التنفيذ المحدد: أسقط (drop) `ThreadPool` `sender`، وقبل أن يتلقّى أي `Worker` خطأً، حاولنا الانضمام (join) لـ `Worker 0`. لم يحصل `Worker 0` بعد على خطأ من `recv`، لذا حُجِب (block) الخيط الرئيسي (main thread)، منتظرًا لـ `Worker 0` لينتهي. في الوقت نفسه، تلقّى `Worker 3` وظيفة (job) ثم تلقّى جميع الخيوط (threads) خطأً. عندما انتهى `Worker 0`، انتظر الخيط الرئيسي (main thread) بقية نسخ (instances) `Worker` لتنتهي. في تلك النقطة، كانوا جميعًا قد خرجوا من حلقاتهم (loops) وتوقّفوا.

تهانينا! الآن أكملنا مشروعنا؛ لدينا خادوم ويب (web server) أساسي يستخدم مجمع خيوط (thread pool) للاستجابة بشكل غير متزامن (asynchronously). نحن قادرون على أداء إيقاف رشيق (graceful shutdown) للخادوم (server)، مما ينظّف جميع الخيوط (threads) في المجمع (pool).

فيما يلي الكود (code) الكامل للمرجع:

<Listing file-name="src/main.rs">

```rust,ignore
{{#rustdoc_include ../listings/ch21-web-server/no-listing-07-final-code/src/main.rs}}
```

</Listing>

<Listing file-name="src/lib.rs">

```rust,noplayground
{{#rustdoc_include ../listings/ch21-web-server/no-listing-07-final-code/src/lib.rs}}
```

</Listing>

يمكننا أن نفعل المزيد هنا! إذا أردت الاستمرار في تحسين هذا المشروع، فيما يلي بعض الأفكار:

- أضف المزيد من التوثيق (documentation) إلى `ThreadPool` وطرقه العامة.
- أضف اختبارات (tests) لوظيفة المكتبة (library).
- غيّر استدعاءات `unwrap` إلى معالجة أخطاء أكثر قوة.
- استخدم `ThreadPool` لأداء بعض المهام غير خدمة طلبات (requests) الويب.
- ابحث عن حزمة (crate) thread pool على [crates.io](https://crates.io/) ونفّذ خادوم ويب (web server) مشابهًا باستخدام الحزمة (crate) بدلاً. ثم، قارن واجهة (API) والمتانة الخاصة بها بمجمع الخيوط (thread pool) الذي نفّذناه.

## الخلاصة (Summary)

أحسنت! لقد وصلت إلى نهاية الكتاب! نريد شكرك لانضمامك لنا في هذه الجولة من Rust. أنت الآن جاهز لتنفيذ مشاريعك الخاصة من Rust والمساعدة مع مشاريع أشخاص آخرين. تذكّر أن هناك مجتمعًا مرحبًا من Rustaceans آخرين يودّون مساعدتك مع أي تحديات تواجهها في رحلتك مع Rust.
