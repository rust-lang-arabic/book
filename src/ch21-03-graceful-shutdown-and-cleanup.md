## الإيقاف الرشيق والتنظيف (Graceful Shutdown and Cleanup)

الكود (code) في القائمة (Listing) 21-20 يستجيب (is responding) للطلبات (requests) بشكل غير متزامن (asynchronously) من خلال (through) استخدام (the use of) مجمع خيوط (a thread pool)، كما (as) قصدنا (we intended). نحصل (We get) على بعض (some) التحذيرات (warnings) حول (about) الحقول (the fields) `workers`، `id`، و (and) `thread` التي (that) لا نستخدمها (we're not using) بطريقة (in a) مباشرة (direct way)، مما يذكّرنا (reminding us) بأننا (that we're) لا ننظّف (not cleaning up) أي شيء (anything). عندما (When) نستخدم (we use) الطريقة (the method) الأقل أناقة (the less elegant) <kbd>ctrl</kbd>-<kbd>C</kbd> لإيقاف (to halt) الخيط الرئيسي (the main thread)، تُوقف (are stopped) جميع (all) الخيوط الأخرى (the other threads) فورًا (immediately) أيضًا (as well)، حتى (even) لو (if) كانت (they were) في منتصف (in the middle of) خدمة (serving) طلب (a request).

بعد ذلك (Next)، إذن (then)، سننفّذ (we'll implement) سمة (the trait) `Drop` لاستدعاء (to call) `join` على (on) كل (each) من (of) الخيوط (the threads) في (in) المجمع (the pool) حتى (so that) يتمكنوا (they can) من إنهاء (finish) الطلبات (the requests) التي (that) يعملون عليها (they're working on) قبل (before) الإغلاق (closing down). ثم (Then)، سننفّذ (we'll implement) طريقة (a way) لإخبار (to tell) الخيوط (the threads) بأنها (that they) يجب أن تتوقّف (should stop) عن قبول (accepting) طلبات (requests) جديدة (new) وتُوقف (and shut down). لرؤية (To see) هذا الكود (this code) أثناء (in) العمل (action)، سنعدّل (we'll modify) خادومنا (our server) ليقبل (to accept) طلبين (two requests) فقط (only) قبل (before) الإيقاف الرشيق (shutting down gracefully) لمجمع خيوطه (its thread pool).

شيء واحد (One thing) يجب ملاحظته (to notice) بينما (as) نذهب (we go): لا يؤثّر (does not affect) أي (any) من (of) أجزاء (the parts of) الكود (the code) التي (that) تتعامل (handle) مع تنفيذ (executing) الإغلاقات (the closures)، لذا (so) كل شيء (everything) هنا (here) سيكون (would be) نفسه (the same) إذا (if) كنا (we were) نستخدم (using) مجمع خيوط (a thread pool) لوقت تشغيل (for an async runtime) غير متزامن (async).

### تطبيق سمة `Drop` على `ThreadPool` (Implementing the `Drop` Trait on `ThreadPool`)

لنبدأ (Let's begin) بتطبيق (with implementing) `Drop` على (on) مجمع خيوطنا (our thread pool). عندما (When) يتم إسقاط (is dropped) المجمع (the pool)، يجب (should) على جميع (all of) خيوطنا (our threads) أن تنضم (join) للتأكّد (to make sure) من أنها (that they) تنهي (finish) عملها (their work). تُظهر (shows) القائمة (Listing) 21-22 محاولة أولى (a first attempt) على تطبيق (at an implementation of) `Drop`؛ لن يعمل (won't quite work) هذا الكود (this code) تمامًا (quite) بعد (yet).

<Listing number="21-22" file-name="src/lib.rs" caption="الانضمام لكل خيط عندما يخرج مجمع الخيوط من النطاق (Joining each thread when the thread pool goes out of scope)">

```rust,ignore,does_not_compile
{{#rustdoc_include ../listings/ch21-web-server/listing-21-22/src/lib.rs:here}}
```

</Listing>

أولاً (First)، نكرّر (we loop) عبر (through) كل (every) من (of) `workers` مجمع الخيوط (the thread pool). نستخدم (We use) `&mut` لهذا (for this) لأن (because) `self` هو (is) مرجع (a reference) قابل للتعديل (mutable)، ونحتاج (and we need) أيضًا (also) إلى أن نتمكّن (to be able) من تعديل (to mutate) `worker`. لكل (For each) `worker`، نطبع (we print) رسالة (a message) تقول (saying) أن (that) هذه (this) نسخة (instance) `Worker` المحددة (particular) تُوقف (is shutting down)، ثم (then) نستدعي (we call) `join` على (on) خيط (the thread of) تلك (that) نسخة (instance) `Worker`. إذا (If) فشل (fails) استدعاء (the call to) `join`، نستخدم (we use) `unwrap` لجعل (to make) Rust تصاب بالذعر (panic) وتذهب (and go) في (into) إيقاف (a shutdown) غير رشيق (ungraceful).

فيما يلي (Here is) الخطأ (the error) الذي (that) نحصل عليه (we get) عندما (when) نُترجم (we compile) هذا الكود (this code):

```console
{{#include ../listings/ch21-web-server/listing-21-22/output.txt}}
```

يخبرنا (tells us) الخطأ (The error) أننا (that we) لا يمكننا (can't) استدعاء (call) `join` لأننا (because we) فقط (only) لدينا (have) استعارة (a borrow) قابلة للتعديل (mutable) من (of) كل (each) `worker` و`join` يأخذ (and `join` takes) ملكية (ownership of) وسيطته (its argument). لحلّ (To solve) هذه المشكلة (this issue)، نحتاج (we need) إلى نقل (to move) الخيط (the thread) خارج (out of) نسخة (the instance) `Worker` التي (that) تمتلك (owns) `thread` بحيث (so that) يتمكّن (can) `join` من استهلاك (consume) الخيط (the thread). إحدى الطرق (One way) للقيام بذلك (to do this) هي (is) أخذ (to take) نفس النهج (the same approach) الذي اتخذناه (that we took) في القائمة (in Listing) 18-15. إذا (If) كان (was) `Worker` يحمل (holding) `Option<thread::JoinHandle<()>>`، يمكننا (we could) استدعاء (call) طريقة (the method) `take` على (on) `Option` لنقل (to move) القيمة (the value) خارج (out of) المتغيّر (the variant) `Some` وترك (and leave) متغيّر (a variant) `None` في مكانه (in its place). بعبارة أخرى (In other words)، `Worker` الذي (that) يعمل (is running) سيكون لديه (would have) متغيّر (a variant) `Some` في (in) `thread`، وعندما (and when) أردنا (we wanted to) تنظيف (clean up) `Worker`، سنستبدل (we'd replace) `Some` بـ (with) `None` بحيث (so that) لن يكون لدى (wouldn't have) `Worker` خيط (a thread) ليشغّله (to run).

ومع ذلك (However)، الوقت الوحيد (the _only_ time) الذي (that) سيأتي (would come up) هذا (this) سيكون (would be) عندما (when) إسقاط (dropping) `Worker`. في المقابل (In exchange)، سنضطر (we'd have to) إلى التعامل (deal with) مع (with) `Option<thread::JoinHandle<()>>` في (in) أي مكان (any place where) وصلنا (we accessed) إلى (to) `worker.thread`. Rust الاصطلاحية (Idiomatic Rust) تستخدم (uses) `Option` قليلاً (quite a bit)، لكن (but) عندما (when) تجد (you find) نفسك (yourself) تُلفّ (wrapping) شيئًا (something) تعلم (you know) أنه (that it) سيكون (will) موجودًا (be present) دائمًا (always) في (in) `Option` كحلّ بديل (as a workaround) مثل هذا (like this)، فهي (it's a) فكرة جيدة (good idea) للبحث (to look for) عن مناهج بديلة (alternative approaches) لجعل (to make) كودك (your code) أنظف (cleaner) وأقل عرضة (and less error-prone) للأخطاء (for errors).

في (In) هذه الحالة (this case)، يوجد (there exists) بديل أفضل (a better alternative): طريقة (the method) `Vec::drain`. تقبل (It accepts) معامل (a parameter) نطاق (range) لتحديد (to specify) أي عناصر (which items) لإزالتها (to remove) من (from) المتجه (the vector) وتُرجع (and returns) مُكرِّرًا (an iterator) من (of) تلك العناصر (those items). سيؤدي تمرير (Passing) بناء (the syntax) `..` range إلى إزالة (will remove) _كل (every)_ قيمة (value) من (from) المتجه (the vector).

لذا (So)، نحتاج (we need) إلى تحديث (to update) تطبيق (the implementation of) `drop` لـ (for) `ThreadPool` مثل هذا (like this):

<Listing file-name="src/lib.rs">

```rust
{{#rustdoc_include ../listings/ch21-web-server/no-listing-04-update-drop-definition/src/lib.rs:here}}
```

</Listing>

يحلّ (resolves) هذا (This) خطأ (the error of) المصرِّف (the compiler) ولا يتطلّب (and does not require) أي (any) تغييرات (changes) أخرى (other) على كودنا (to our code). لاحظ (Note) أنه، لأن (that, because) يمكن استدعاء (can be called) drop عند (when) الذعر (panicking)، يمكن (could) أن يصاب (panic) unwrap أيضًا بالذعر (also) ويتسبّب (and cause) في ذعر مزدوج (a double panic)، مما (which) الذي يُعطّل (crashes) البرنامج (the program) فورًا (immediately) وينهي (and ends) أي (any) تنظيف (cleanup) جارٍ (in progress). هذا (This) جيد (is fine) لبرنامج مثال (for an example program)، لكن (but) ليس (isn't) لا يُنصح به (recommended) لكود (for code) إنتاجي (production).

### الإشارة للخيوط للتوقف عن الاستماع للوظائف (Signaling to the Threads to Stop Listening for Jobs)

مع (With) جميع (all) التغييرات (the changes) التي أجريناها (we've made)، يُترجم (compiles) كودنا (our code) بدون (without) أي (any) تحذيرات (warnings). ومع ذلك (However)، الأخبار السيئة (the bad news) هي (is) أن (that) هذا الكود (this code) لا يعمل (doesn't function) بالطريقة (the way) التي نريدها (we want it to) بعد (yet). المفتاح (The key) هو (is) المنطق (the logic) في (in) الإغلاقات (the closures) التي (that) يُشغّلها (are run by) الخيوط (the threads) من (of) نسخ (the instances of) `Worker`: في الوقت الحالي (At the moment)، نستدعي (we call) `join`، لكن (but) ذلك (that) لن يُوقف (won't shut down) الخيوط (the threads)، لأنها (because they) تُكرّر (loop) `loop` للأبد (forever) بحثًا (looking) عن وظائف (for jobs). إذا (If) حاولنا (we try to) إسقاط (drop) `ThreadPool` الخاص بنا (our) مع (with) تطبيقنا الحالي (our current implementation) لـ (of) `drop`، فسيُحجَب (will block) الخيط الرئيسي (the main thread) للأبد (forever)، منتظرًا (waiting) للخيط الأول (for the first thread) لينتهي (to finish).

لإصلاح (To fix) هذه المشكلة (this problem)، سنحتاج (we'll need) إلى تغيير (a change) في (in) تطبيق (the implementation of) `drop` لـ (for) `ThreadPool` ثم (and then) تغيير (a change) في (in) حلقة (the loop of) `Worker`.

أولاً (First)، سنغيّر (we'll change) تطبيق (the implementation of) `drop` لـ (for) `ThreadPool` لإسقاط (to drop) `sender` صراحةً (explicitly) قبل (before) الانتظار (waiting) للخيوط (for the threads) لتنتهي (to finish). تُظهر (shows) القائمة (Listing) 21-23 التغييرات (the changes) على (to) `ThreadPool` لإسقاط (to drop) `sender` صراحةً (explicitly). على عكس (Unlike) مع (with) الخيط (the thread)، هنا (here) نحتاج فعلاً (_do_ need) إلى استخدام (to use) `Option` لنتمكّن (to be able) من نقل (to move) `sender` خارج (out of) `ThreadPool` مع (with) `Option::take`.

<Listing number="21-23" file-name="src/lib.rs" caption="إسقاط `sender` صراحةً قبل الانضمام لخيوط `Worker` (Explicitly dropping `sender` before joining the `Worker` threads)">

```rust,noplayground,not_desired_behavior
{{#rustdoc_include ../listings/ch21-web-server/listing-21-23/src/lib.rs:here}}
```

</Listing>

يُغلق (Dropping) `sender` القناة (the channel)، مما يُشير (which indicates) إلى أنه (that) لن يتم إرسال (will be sent) المزيد من الرسائل (no more messages). عندما (When) يحدث ذلك (that happens)، ستُرجع (will return) جميع (all) الاستدعاءات (the calls) لـ (to) `recv` التي (that) تقوم بها (do) نسخ (the instances of) `Worker` في (in) الحلقة اللانهائية (the infinite loop) خطأً (an error). في القائمة (In Listing) 21-24، نُغيّر (we change) حلقة (the loop of) `Worker` للخروج (to exit) من الحلقة (from the loop) بشكل رشيق (gracefully) في (in) تلك الحالة (that case)، مما يعني (which means) أن (that) الخيوط (the threads) ستنتهي (will finish) عندما (when) يستدعي (calls) تطبيق (the implementation of) `drop` لـ (for) `ThreadPool` `join` عليها (on them).

<Listing number="21-24" file-name="src/lib.rs" caption="الخروج صراحةً من الحلقة عندما تُرجع `recv` خطأً (Explicitly exiting the loop when `recv` returns an error)">

```rust,noplayground
{{#rustdoc_include ../listings/ch21-web-server/listing-21-24/src/lib.rs:here}}
```

</Listing>

لرؤية (To see) هذا الكود (this code) أثناء العمل (in action)، لنعدّل (let's modify) `main` ليقبل (to accept) طلبين (two requests) فقط (only) قبل (before) إيقاف (shutting down) الخادوم (the server) بشكل رشيق (gracefully)، كما (as) موضح (shown) في القائمة (in Listing) 21-25.

<Listing number="21-25" file-name="src/main.rs" caption="إيقاف الخادوم بعد خدمة طلبين عن طريق الخروج من الحلقة (Shutting down the server after serving two requests by exiting the loop)">

```rust,ignore
{{#rustdoc_include ../listings/ch21-web-server/listing-21-25/src/main.rs:here}}
```

</Listing>

لن تريد (You wouldn't want) أن (that) خادوم ويب (a web server) حقيقي (real-world) يُوقف (shut down) بعد (after) خدمة (serving) طلبين (two requests) فقط (only). هذا الكود (This code) فقط (just) يوضّح (demonstrates) أن (that) الإيقاف الرشيق (the graceful shutdown) والتنظيف (and cleanup) في حالة عمل جيدة (are in working order).

طريقة (The method) `take` محددة (is defined) في (in) سمة (the trait) `Iterator` وتحدّ (and limits) التكرار (the iteration) لأول (to at most) العنصرين اثنين (two items) الأولين (the first). سيخرج (will go out) `ThreadPool` من النطاق (of scope) في نهاية (at the end of) `main`، وسيُشغَّل (and will run) تطبيق (the implementation of) `drop`.

ابدأ (Start) الخادوم (the server) مع (with) `cargo run` واعمل (and make) ثلاثة (three) طلبات (requests). يجب (should) على الطلب (The request) الثالث (third) أن يُخطئ (error)، وفي (and in) طرفيتك (your terminal)، يجب (should) أن ترى (you see) إخراجًا (output) مشابهًا (similar) لهذا (to this):

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

قد ترى (You might see) ترتيبًا (an ordering) مختلفًا (different) من (of) معرّفات (the IDs of) `Worker` والرسائل (and messages) المطبوعة (printed). يمكننا أن نرى (We can see) كيفية عمل (how works) هذا الكود (this code) من (from) الرسائل (the messages): حصل (got) النسخ (the instances) `Worker` 0 و (and) 3 على (on) أول (the first) طلبين اثنين (two requests). توقّف (stopped) الخادوم (The server) عن قبول (accepting) الاتصالات (connections) بعد (after) الاتصال الثاني (the second connection)، وبدأ (and starts) تطبيق (the implementation of) `Drop` على (on) `ThreadPool` في التنفيذ (executing) قبل (before) أن يبدأ (starts) `Worker 3` حتى (even) وظيفته (its job). يقطع الاتصال (Dropping) `sender` جميع (all) نسخ (the instances of) `Worker` ويخبرها (and tells them) لتُوقف (to shut down). تطبع (print) نسخ (The instances of) `Worker` كل (every) رسالة (message) عندما (when) تقطع الاتصال (they disconnect)، ثم (and then) يستدعي (calls) مجمع الخيوط (the thread pool) `join` لانتظار (to wait for) كل (every) خيط (thread of) `Worker` لينتهي (to finish).

لاحظ (Notice) جانبًا واحدًا (one aspect) مثيرًا للاهتمام (interesting) من (of) هذا التنفيذ المحدد (this particular execution): أسقط (dropped) `ThreadPool` `sender`، وقبل (and before) أن يتلقّى (received) أي (any) `Worker` خطأً (an error)، حاولنا (we tried) الانضمام (to join) لـ (to) `Worker 0`. لم يحصل (had not yet gotten) `Worker 0` بعد (yet) على خطأ (an error) من (from) `recv`، لذا (so) حُجِب (blocked) الخيط الرئيسي (the main thread)، منتظرًا (waiting) لـ (for) `Worker 0` لينتهي (to finish). في الوقت نفسه (At the meantime)، تلقّى (received) `Worker 3` وظيفة (a job) ثم (and then) تلقّى (received) جميع (all) الخيوط (the threads) خطأً (an error). عندما (When) انتهى (finished) `Worker 0`، انتظر (waited) الخيط الرئيسي (the main thread) بقية (the rest of) نسخ (the instances of) `Worker` لتنتهي (to finish). في (At) تلك النقطة (that point)، كانوا (they had) جميعًا (all) قد خرجوا (exited) من حلقاتهم (from their loops) وتوقّفوا (and stopped).

تهانينا (Congrats)! الآن (Now) أكملنا (we've completed) مشروعنا (our project)؛ لدينا (we have) خادوم ويب (a web server) أساسي (basic) يستخدم (that uses) مجمع خيوط (a thread pool) للاستجابة (to respond) بشكل غير متزامن (asynchronously). نحن (We're) قادرون (able) على أداء (to perform) إيقاف (a shutdown) رشيق (graceful) للخادوم (of the server)، مما (which) ينظّف (cleans up) جميع (all) الخيوط (the threads) في المجمع (in the pool).

فيما يلي (Here's) الكود الكامل (the full code) للمرجع (for reference):

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

يمكننا أن نفعل (We could do) المزيد (more) هنا (here)! إذا (If) أردت (you want) الاستمرار (to continue) في تحسين (enhancing) هذا المشروع (this project)، فيما يلي (here are) بعض الأفكار (some ideas):

- أضف (Add) المزيد (more) من التوثيق (documentation) إلى (to) `ThreadPool` وطرقه (and its methods) العامة (public).
- أضف (Add) اختبارات (tests) لوظيفة (for the functionality of) المكتبة (the library).
- غيّر (Change) استدعاءات (calls to) `unwrap` إلى (to) معالجة (handling) أخطاء (error) أكثر قوة (more robust).
- استخدم (Use) `ThreadPool` لأداء (to perform) بعض (some) المهام (task) غير (other than) خدمة (serving) طلبات (requests) الويب (web).
- ابحث (Find) عن حزمة (a crate) thread pool على (on) [crates.io](https://crates.io/) ونفّذ (and implement) خادوم ويب (a web server) مشابهًا (similar) باستخدام (using) الحزمة (the crate) بدلاً (instead). ثم (Then)، قارن (compare) واجهة (the API) والمتانة (and robustness) الخاصة بها (of it) بمجمع الخيوط (with the thread pool) الذي نفّذناه (that we implemented).

## الخلاصة (Summary)

أحسنت (Well done)! لقد وصلت (You've made it) إلى نهاية (to the end of) الكتاب (the book)! نريد (We want) شكرك (to thank you) لانضمامك (for joining) لنا (us) في (on) هذه الجولة (this tour) من (of) Rust. أنت (You're) الآن (now) جاهز (ready) لتنفيذ (to implement) مشاريعك الخاصة (your own projects) من (of) Rust والمساعدة (and help) مع (with) مشاريع (the projects of) أشخاص آخرين (other people). تذكّر (Keep in mind) أن (that) هناك (there is) مجتمعًا (a community) مرحبًا (welcoming) من (of) Rustaceans آخرين (other) يودّون (who would love to) مساعدتك (help you) مع (with) أي (any) تحديات (challenges) تواجهها (you encounter) في رحلتك (on your journey) مع (with) Rust.
