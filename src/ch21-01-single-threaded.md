## بناء خادوم ويب أحادي الخيط (Building a Single-Threaded Web Server)

سنبدأ (we'll start) بتشغيل (by getting working) خادوم ويب (web server) أحادي الخيط (single-threaded). قبل أن نبدأ (before we begin)، دعونا نلقي (let's look at) نظرة سريعة (a quick overview) على البروتوكولات (protocols) المستخدمة (involved) في بناء (in building) خوادم الويب (web servers). تفاصيل (the details of) هذه البروتوكولات (these protocols) خارج نطاق (are beyond the scope of) هذا الكتاب (this book)، ولكن (but) نظرة عامة موجزة (a brief overview) ستعطيك (will give you) المعلومات (the information) التي تحتاجها (you need).

البروتوكولان الرئيسيان (the two main protocols) المستخدمان (involved) في خوادم الويب (in web servers) هما (are) _Hypertext Transfer Protocol_ _(HTTP)_ و (and) _Transmission Control Protocol_ _(TCP)_. كلا البروتوكولين (both protocols) هما (are) بروتوكولا (protocols) _request-response_ طلب-استجابة (request-response)، مما يعني (meaning) أن (that) _client_ (عميل) (a client) يبدأ (initiates) الطلبات (requests) و (and) _server_ (خادوم) (a server) يستمع (listens) للطلبات (to the requests) ويوفر (and provides) استجابة (a response) للعميل (to the client). محتويات (the contents of) تلك الطلبات والاستجابات (those requests and responses) محددة (are defined) بواسطة البروتوكولات (by the protocols).

TCP هو (is) البروتوكول (the protocol) ذو المستوى الأدنى (the lower-level) الذي يصف (that describes) تفاصيل (the details of) كيفية (how) انتقال (gets) المعلومات (information) من خادوم (from one server) إلى آخر (to another) ولكنه (but) لا يحدد (doesn't specify) ما هي (what) تلك المعلومات (that information is). يبني (builds) HTTP على (on top of) TCP من خلال (by) تحديد (defining) محتويات (the contents of) الطلبات والاستجابات (the requests and responses). من الممكن تقنيًا (it's technically possible) استخدام (to use) HTTP مع (with) بروتوكولات أخرى (other protocols)، ولكن (but) في الغالبية العظمى (in the vast majority) من الحالات (of cases)، يرسل (sends) HTTP بياناته (its data) عبر (over) TCP. سنعمل (we'll work) مع (with) البايتات الخام (the raw bytes) لطلبات واستجابات (of TCP and HTTP requests and responses) TCP و HTTP.

### الاستماع لاتصال TCP (Listening to the TCP Connection)

يحتاج (needs) خادوم الويب الخاص بنا (our web server) إلى (to) الاستماع (listening) لاتصال (to a TCP connection) TCP، لذا (so) فهذا هو (that's) الجزء الأول (the first part) الذي سنعمل عليه (we'll work on). توفر (provides) المكتبة القياسية (the standard library) وحدة (a module) `std::net` تتيح لنا (that lets us) القيام بذلك (do this). لنصنع (let's make) مشروعًا جديدًا (a new project) بالطريقة المعتادة (in the usual way):

```console
$ cargo new hello
     Created binary (application) `hello` project
$ cd hello
```

الآن (now) أدخل (enter) الكود (the code) في القائمة (in Listing) 21-1 في (in) _src/main.rs_ للبدء (to start). سيستمع (will listen) هذا الكود (this code) عند العنوان المحلي (at the local address) `127.0.0.1:7878` للتدفقات الواردة (for incoming TCP streams) incoming TCP streams. عندما (when) يحصل على (it gets) تدفق وارد (an incoming stream)، سيطبع (it will print) `Connection established!`.

<Listing number="21-1" file-name="src/main.rs" caption="الاستماع (listening) للتدفقات الواردة (for incoming streams) وطباعة (and printing) رسالة (a message) عندما (when) نستقبل (we receive) تدفقًا (a stream)">

```rust,no_run
{{#rustdoc_include ../listings/ch21-web-server/listing-21-01/src/main.rs}}
```

</Listing>

باستخدام (using) `TcpListener`، يمكننا (we can) الاستماع (listen) لاتصالات (for TCP connections) TCP على العنوان (at the address) `127.0.0.1:7878`. في العنوان (in the address)، القسم (the section) قبل النقطتين (before the colon) هو (is) عنوان (an IP address) IP يمثل (representing) جهاز الكمبيوتر الخاص بك (your computer) (هذا هو نفسه (this is the same) على كل جهاز كمبيوتر (on every computer) ولا يمثل (and doesn't represent) كمبيوتر المؤلفين (the authors' computer) بشكل خاص (specifically))، و (and) `7878` هو (is) المنفذ (the port). اخترنا (we chose) هذا المنفذ (this port) لسببين (for two reasons): لا يتم قبول (is not normally accepted) HTTP عادة (normally) على هذا المنفذ (on this port)، لذا (so) فإن (that) خادومنا (our server) من غير المحتمل (is unlikely) أن يتعارض (to conflict) مع (with) أي خادوم ويب آخر (any other web server) قد يكون لديك (you might have) قيد التشغيل (running) على جهازك (on your machine)، و (and) 7878 هو (is) _rust_ مكتوبة (typed) على الهاتف (on a telephone).

تعمل (works) دالة (the function) `bind` في هذا السيناريو (in this scenario) مثل (like) دالة (the function) `new` من حيث (in that) أنها (it) ستُرجع (will return) نسخة جديدة (a new instance) من (of) `TcpListener`. تُسمى (is called) الدالة (the function) `bind` لأنه (because)، في الشبكات (in networking)، الاتصال بمنفذ (connecting to a port) للاستماع (to listen to) يُعرف باسم (is known as) "binding to a port" (ربط بمنفذ) (binding to a port).

تُرجع (returns) دالة (the function) `bind` نتيجة (a Result) `Result<T, E>`، مما يشير إلى (which indicates) أنه (that) من الممكن (it's possible) أن يفشل (that binding could fail) الربط (binding)، على سبيل المثال (for example)، إذا (if) قمنا بتشغيل (we ran) نسختين (two instances) من برنامجنا (of our program) وبالتالي (and thus) كان لدينا (we had) برنامجان (two programs) يستمعان (listening) إلى نفس المنفذ (to the same port). نظرًا لأننا (because we're) نكتب (writing) خادومًا أساسيًا (a basic server) فقط (only) لأغراض التعلم (for learning purposes)، فلن نقلق (we won't worry) بشأن (about) معالجة (handling) هذه الأنواع (these kinds) من الأخطاء (of errors)؛ بدلاً من ذلك (instead)، نستخدم (we use) `unwrap` لإيقاف (to stop) البرنامج (the program) إذا (if) حدثت (occur) أخطاء (errors).

تُرجع (returns) الطريقة (the method) `incoming` على (on) `TcpListener` مُكرِّرًا (an iterator) يعطينا (that gives us) تسلسلاً (a sequence) من التدفقات (of streams) (بشكل أكثر تحديدًا (more specifically)، تدفقات (streams) من نوع (of type) `TcpStream`). _stream_ (تدفق) (a single stream) واحد (one) يمثل (represents) اتصالاً مفتوحًا (an open connection) بين العميل والخادوم (between the client and the server). _Connection_ (اتصال) (a connection) هو (is) الاسم (the name) لعملية (for the process of) الطلب والاستجابة (the request and response) الكاملة (the full) التي (in which) يتصل فيها (connects) العميل (a client) بالخادوم (to the server)، ويولد (generates) الخادوم (the server) استجابة (a response)، ويغلق (and closes) الخادوم (the server) الاتصال (the connection). على هذا النحو (as such)، سنقرأ (we'll read) من (from) `TcpStream` لنرى (to see) ما (what) أرسله (sent) العميل (the client) ثم (then) نكتب (write) استجابتنا (our response) إلى التدفق (to the stream) لإرسال (to send) البيانات (the data) مرة أخرى (back) إلى العميل (to the client). بشكل عام (overall)، ستعالج (will handle) حلقة (this for loop) `for` هذه (this) كل اتصال (each connection) بدوره (in turn) وتنتج (and produce) سلسلة (a series) من التدفقات (of streams) لنتعامل معها (for us to handle).

في الوقت الحالي (for now)، تتكون (consists of) معالجتنا (our handling) للتدفق (of the stream) من (of) استدعاء (calling) `unwrap` لإنهاء (to terminate) برنامجنا (our program) إذا (if) كان للتدفق (the stream has) أي أخطاء (any errors)؛ إذا (if) لم تكن هناك (there are no) أخطاء (errors)، يطبع (prints) البرنامج (the program) رسالة (a message). سنضيف (we'll add) المزيد (more) من الوظائف (functionality) لحالة النجاح (for the success case) في القائمة التالية (in the next listing). السبب في (the reason why) أننا (we) قد نتلقى (might receive) أخطاء (errors) من (from) طريقة (the method) `incoming` عندما (when) يتصل (connects) عميل (a client) بالخادوم (to the server) هو (is) أننا (that we're) لا نكرر (not actually iterating) فعليًا (actually) على الاتصالات (over connections). بدلاً من ذلك (instead)، نكرر (we're iterating) على (over) _محاولات اتصال_ (connection attempts). قد لا يكون (might not be) الاتصال (the connection) ناجحًا (successful) لعدة أسباب (for a number of reasons)، الكثير منها (many of them) خاص (are specific) بنظام التشغيل (to the operating system). على سبيل المثال (for example)، للعديد (many) من أنظمة التشغيل (operating systems) حد (have a limit) لعدد (to the number of) الاتصالات المفتوحة المتزامنة (simultaneous open connections) التي يمكنها (they can) دعمها (support)؛ ستنتج (will produce) محاولات الاتصال الجديدة (new connection attempts) التي تتجاوز (that go beyond) هذا العدد (that number) خطأ (an error) حتى (until) يتم إغلاق (are closed) بعض (some of) الاتصالات المفتوحة (the open connections).

لنحاول (let's try) تشغيل (running) هذا الكود (this code)! استدعِ (invoke) `cargo run` في الطرفية (in the terminal)، ثم (then) قم بتحميل (load) _127.0.0.1:7878_ في (in) متصفح الويب (a web browser). يجب (should) أن يعرض (display) المتصفح (the browser) رسالة خطأ (an error message) مثل (like) "Connection reset" لأن (because) الخادوم (the server) لا يرسل (isn't currently sending) حاليًا (currently) أي بيانات (any data). ولكن (but) عندما (when) تنظر (you look) إلى (at) طرفيتك (your terminal)، يجب (should) أن ترى (see) عدة رسائل (several messages) تمت طباعتها (printed) عندما (when) اتصل (connected) المتصفح (the browser) بالخادوم (to the server)!

```text
     Running `target/debug/hello`
Connection established!
Connection established!
Connection established!
```

في بعض الأحيان (sometimes) سترى (you'll see) رسائل متعددة (multiple messages) مطبوعة (printed) لطلب (for one browser request) متصفح (browser) واحد (one)؛ قد يكون السبب (the reason might be) هو أن (that) المتصفح (the browser) يقدم (is making) طلبًا (a request) للصفحة (for the page) بالإضافة إلى (as well as) طلب (a request) لموارد أخرى (for other resources)، مثل (such as) أيقونة (the icon) _favicon.ico_ التي تظهر (that appears) في علامة تبويب (in the browser tab) المتصفح (browser).

قد يكون أيضًا (it could also be) أن (that) المتصفح (the browser) يحاول (is trying) الاتصال (to connect) بالخادوم (to the server) عدة مرات (multiple times) لأن (because) الخادوم (the server) لا يستجيب (isn't responding) بأي بيانات (with any data). عندما (when) يخرج (goes out of) `stream` من النطاق (scope) ويتم إسقاطه (and gets dropped) في نهاية (at the end of) الحلقة (the loop)، يتم إغلاق (is closed) الاتصال (the connection) كجزء (as part) من (of) تطبيق (the drop implementation) `drop`. تتعامل (deal with) المتصفحات (browsers) أحيانًا (sometimes) مع (with) الاتصالات المغلقة (closed connections) عن طريق (by) إعادة المحاولة (retrying)، لأن (because) المشكلة (the problem) قد تكون (might be) مؤقتة (temporary).

تفتح (open) المتصفحات (browsers) أيضًا (also) في بعض الأحيان (sometimes) اتصالات متعددة (multiple connections) بالخادوم (to the server) دون (without) إرسال (sending) أي طلبات (any requests) بحيث (so that) إذا (if) أرسلت (they send) طلبات (requests) لاحقًا (later)، يمكن (can) أن تحدث (happen) هذه الطلبات (those requests) بشكل أسرع (faster). عندما (when) يحدث هذا (this happens)، سيرى (will see) خادومنا (our server) كل اتصال (every connection)، بغض النظر (regardless) عما إذا كانت (whether) هناك (there are) أي طلبات (any requests) عبر ذلك الاتصال (over that connection). تقوم (do) العديد (many) من إصدارات (versions of) المتصفحات المستندة إلى (browsers based on) Chrome بذلك (this)، على سبيل المثال (for example)؛ يمكنك (you can) تعطيل (disable) هذا التحسين (this optimization) باستخدام (by using) وضع التصفح الخاص (private browsing mode) أو (or) استخدام (using) متصفح مختلف (a different browser).

العامل المهم (the important factor) هو (is) أننا (that we) نجحنا (succeeded) في الحصول على (in getting) مقبض (a handle) لاتصال (to a TCP connection) TCP!

تذكر (remember) إيقاف (to stop) البرنامج (the program) بالضغط على (by pressing) <kbd>ctrl</kbd>-<kbd>C</kbd> عندما (when) تنتهي (you're finished) من تشغيل (running) إصدار معين (a particular version) من الكود (of the code). ثم (then) أعد تشغيل (restart) البرنامج (the program) عن طريق (by) استدعاء (invoking) أمر (the command) `cargo run` بعد (after) إجراء (making) كل مجموعة (each set) من (of) تغييرات (code changes) الكود (code) للتأكد (to make sure) من أنك (you're) تشغل (running) أحدث كود (the newest code).

### قراءة الطلب (Reading the Request)

لنطبق (let's implement) الوظيفة (the functionality) لقراءة (for reading) الطلب (the request) من المتصفح (from the browser)! لفصل (to separate) المهام (the concerns) المتمثلة في (of) الحصول (first getting) أولاً (first) على اتصال (a connection) ثم (then) اتخاذ (taking) بعض الإجراءات (some action) مع الاتصال (with the connection)، سنبدأ (we'll start) دالة جديدة (a new function) لمعالجة (for processing) الاتصالات (connections). في (in) دالة (this new function) `handle_connection` الجديدة (new) هذه (this)، سنقرأ (we'll read) البيانات (the data) من (from) تدفق (the TCP stream) TCP ونطبعها (and print it) حتى (so) نتمكن (we can) من رؤية (see) البيانات المرسلة (the data being sent) من المتصفح (from the browser). غيّر (change) الكود (the code) ليبدو (to look) مثل (like) القائمة (Listing) 21-2.

<Listing number="21-2" file-name="src/main.rs" caption="القراءة (reading) من (from) `TcpStream` وطباعة (and printing) البيانات (the data)">

```rust,no_run
{{#rustdoc_include ../listings/ch21-web-server/listing-21-02/src/main.rs}}
```

</Listing>

نجلب (we bring) `std::io::BufReader` و (and) `std::io::prelude` إلى النطاق (into scope) للوصول إلى (to get access to) السمات (traits) والأنواع (and types) التي تتيح لنا (that let us) القراءة من (read from) والكتابة إلى (and write to) التدفق (the stream). في (in) حلقة (the for loop) `for` في (in) دالة (the function) `main`، بدلاً من (instead of) طباعة (printing) رسالة (a message) تقول (that says) إننا (we) أنشأنا (made) اتصالاً (a connection)، نستدعي (we now call) الآن (now) دالة (the new function) `handle_connection` الجديدة (new) ونمرر (and pass) `stream` إليها (to it).

في (in) دالة (the function) `handle_connection`، نُنشئ (we create) نسخة جديدة (a new instance) من (of) `BufReader` تلتف (that wraps) حول (around) مرجع (a reference) إلى (to) `stream`. يضيف (adds) `BufReader` التخزين المؤقت (buffering) عن طريق (by) إدارة (managing) الاستدعاءات (calls) لطرق (to the methods of) سمة (the trait) `std::io::Read` لنا (for us).

نُنشئ (we create) متغيرًا (a variable) باسم (named) `http_request` لجمع (to collect) أسطر (the lines of) الطلب (the request) التي يرسلها (that sends) المتصفح (the browser) إلى خادومنا (to our server). نشير إلى (we indicate) أننا (that we) نريد (want) جمع (to collect) هذه الأسطر (these lines) في (in) متجه (a vector) عن طريق (by) إضافة (adding) توضيح النوع (the type annotation) `Vec<_>`.

يطبق (implements) `BufReader` سمة (the trait) `std::io::BufRead`، والتي (which) توفر (provides) طريقة (the method) `lines`. تُرجع (returns) طريقة (the method) `lines` مُكرِّرًا (an iterator) لـ (of) `Result<String, std::io::Error>` عن طريق (by) تقسيم (splitting) تدفق (the stream of) البيانات (data) كلما (whenever) رأى (it sees) بايت (a newline byte) سطر جديد (newline). للحصول على (to get) كل (each) `String`، نستخدم (we use) `map` و (and) `unwrap` لكل (on each) `Result`. قد يكون (could be) `Result` خطأً (an error) إذا (if) لم تكن (wasn't) البيانات (the data) UTF-8 صالحة (valid) أو (or) إذا (if) كانت هناك (there was) مشكلة (a problem) في القراءة (reading) من التدفق (from the stream). مرة أخرى (again)، يجب على (should) البرنامج الإنتاجي (a production program) معالجة (handle) هذه الأخطاء (these errors) بشكل أكثر رشاقة (more gracefully)، لكننا (but we're) نختار (choosing) إيقاف (to stop) البرنامج (the program) في حالة الخطأ (in the error case) من أجل البساطة (for simplicity).

يشير (signals) المتصفح (the browser) إلى (the) نهاية (end of) طلب (an HTTP request) HTTP عن طريق (by) إرسال (sending) حرفي (two newline characters) سطر جديد (newline) متتاليين (in a row)، لذلك (so) للحصول على (to get) طلب واحد (one request) من التدفق (from the stream)، نأخذ (we take) الأسطر (the lines) حتى (until) نحصل على (we get to) سطر فارغ (a line that is the empty string). بمجرد (once) جمع (we've collected) الأسطر (the lines) في المتجه (in the vector)، نطبعها (we're printing them) باستخدام (using) تنسيق التصحيح الجميل (pretty debug formatting) حتى (so) نتمكن (we can) من إلقاء نظرة على (take a look at) التعليمات (the instructions) التي يرسلها (that is sending) متصفح الويب (the web browser) إلى خادومنا (to our server).

لنجرب (let's try) هذا الكود (this code)! ابدأ (start) البرنامج (the program) واطلب (and make a request) في (in) متصفح الويب (a web browser) مرة أخرى (again). لاحظ (note) أننا (that we) سنظل (will still) نحصل على (get) صفحة خطأ (an error page) في المتصفح (in the browser)، لكن (but) إخراج (the output of) برنامجنا (our program) في الطرفية (in the terminal) سيبدو (will now look) الآن (now) مشابهًا (similar) لهذا (to this):

<!-- manual-regeneration
cd listings/ch21-web-server/listing-21-02
cargo run
make a request to 127.0.0.1:7878
Can't automate because the output depends on making requests
-->

```console
$ cargo run
   Compiling hello v0.1.0 (file:///projects/hello)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.42s
     Running `target/debug/hello`
Request: [
    "GET / HTTP/1.1",
    "Host: 127.0.0.1:7878",
    "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:99.0) Gecko/20100101 Firefox/99.0",
    "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language: en-US,en;q=0.5",
    "Accept-Encoding: gzip, deflate, br",
    "DNT: 1",
    "Connection: keep-alive",
    "Upgrade-Insecure-Requests: 1",
    "Sec-Fetch-Dest: document",
    "Sec-Fetch-Mode: navigate",
    "Sec-Fetch-Site: none",
    "Sec-Fetch-User: ?1",
    "Cache-Control: max-age=0",
]
```

اعتمادًا على (depending on) متصفحك (your browser)، قد تحصل على (you may get) إخراج (output) مختلف قليلاً (slightly different). الآن (now) بعد أن (that) نطبع (we're printing) بيانات الطلب (the request data)، يمكننا (we can) معرفة (see) سبب (why) حصولنا على (we're getting) اتصالات متعددة (multiple connections) من (from) طلب (one browser request) متصفح (browser) واحد (one) من خلال (by) النظر إلى (looking at) المسار (the path) بعد (after) `GET` في السطر الأول (in the first line) من الطلب (of the request). إذا (if) كانت (were) الاتصالات المتكررة (the repeated connections) تطلب (all requesting) جميعها (all) _/_، فنحن (we) نعلم (know) أن (that) المتصفح (the browser) يحاول (is trying) جلب (to fetch) _/_ بشكل متكرر (repeatedly) لأنه (because) لا يحصل على (it's not getting) استجابة (a response) من برنامجنا (from our program).

لنحلل (let's break down) بيانات الطلب (this request data) هذه (this) لفهم (to understand) ما (what) يطلبه (is asking for) المتصفح (the browser) من برنامجنا (from our program).

<!-- Old headings. Do not remove or links may break. -->

<a id="a-closer-look-at-an-http-request"></a>
<a id="looking-closer-at-an-http-request"></a>

### نظرة أقرب على طلب HTTP (A Closer Look at an HTTP Request)

HTTP هو (is) بروتوكول (a protocol) نصي (text-based)، والطلب (and a request) يأخذ (takes) هذا التنسيق (this format):

```text
Method Request-URI HTTP-Version CRLF
headers CRLF
message-body
```

السطر الأول (the first line) هو (is) _request line_ (سطر الطلب) (the request line) الذي يحمل (that holds) معلومات (information) حول (about) ما (what) يطلبه (is requesting) العميل (the client). يشير (indicates) الجزء الأول (the first part) من (of) سطر الطلب (the request line) إلى (to) الطريقة (the method) المستخدمة (being used)، مثل (such as) `GET` أو (or) `POST`، والتي (which) تصف (describes) كيف (how) يقدم (is making) العميل (the client) هذا الطلب (this request). استخدم (used) عميلنا (our client) طلب (a GET request) `GET`، مما يعني (which means) أنه (it) يطلب (is asking for) معلومات (information).

الجزء التالي (the next part) من (of) سطر الطلب (the request line) هو (is) _/_، والذي (which) يشير إلى (indicates) _uniform resource identifier_ _(URI)_ (معرّف الموارد الموحد) (the uniform resource identifier) الذي يطلبه (that is requesting) العميل (the client): URI يكاد يكون (is almost)، ولكن (but) ليس تمامًا (not quite)، مثل (the same as) _uniform resource locator_ _(URL)_ (محدد موقع الموارد الموحد) (a uniform resource locator). الفرق (the difference) بين (between) URIs و (and) URLs ليس مهمًا (isn't important) لأغراضنا (for our purposes) في هذا الفصل (in this chapter)، ولكن (but) مواصفات (the HTTP specification) HTTP تستخدم (uses) مصطلح (the term) _URI_، لذا (so) يمكننا (we can) فقط (just) استبدال (substitute) _URL_ ذهنيًا (mentally) بـ (for) _URI_ هنا (here).

الجزء الأخير (the last part) هو (is) إصدار (the HTTP version) HTTP الذي يستخدمه (uses) العميل (the client)، ثم (and then) ينتهي (ends) سطر الطلب (the request line) بتسلسل (with a CRLF sequence) CRLF. (_CRLF_ تعني (stands for) _carriage return_ و (and) _line feed_، وهي (which are) مصطلحات (terms) من أيام (from the days of) الآلة الكاتبة (the typewriter)!) يمكن (can) أيضًا (also) كتابة (be written) تسلسل (the CRLF sequence) CRLF على شكل (as) `\r\n`، حيث (where) `\r` هو (is) carriage return و (and) `\n` هو (is) line feed. يفصل (separates) _CRLF sequence_ (تسلسل CRLF) (the CRLF sequence) سطر الطلب (the request line) عن (from) بقية (the rest of) بيانات الطلب (the request data). لاحظ (note) أنه (that) عندما (when) يتم طباعة (is printed) CRLF، نرى (we see) بداية (a new line start) سطر جديد (new line) بدلاً من (instead of) `\r\n`.

بالنظر إلى (looking at) بيانات (the data of) سطر الطلب (the request line) التي تلقيناها (we've received) من تشغيل (from running) برنامجنا (our program) حتى الآن (so far)، نرى (we see) أن (that) `GET` هو (is) الطريقة (the method)، _/_ هو (is) URI الطلب (the request URI)، و (and) `HTTP/1.1` هو (is) الإصدار (the version).

بعد (after) سطر الطلب (the request line)، الأسطر المتبقية (the remaining lines) بدءًا من (starting from) `Host:` فصاعدًا (onward) هي (are) الرؤوس (headers). طلبات (GET requests) `GET` ليس لها (have no) جسم (body).

حاول (try) تقديم (making) طلب (a request) من (from) متصفح مختلف (a different browser) أو (or) طلب (asking for) عنوان مختلف (a different address)، مثل (such as) _127.0.0.1:7878/test_، لترى (to see) كيف (how) تتغير (changes) بيانات الطلب (the request data).

الآن (now) بعد أن (that) عرفنا (we know) ما (what) يطلبه (is asking for) المتصفح (the browser)، لنرسل (let's send back) بعض البيانات (some data)!

### كتابة استجابة (Writing a Response)

سنطبق (we'll implement) إرسال (sending) البيانات (data) في (in) استجابة (a response) لطلب (to a client request) العميل (client). الاستجابات (responses) لها (have) التنسيق التالي (the following format):

```text
HTTP-Version Status-Code Reason-Phrase CRLF
headers CRLF
message-body
```

السطر الأول (the first line) هو (is) _status line_ (سطر الحالة) (a status line) الذي يحتوي على (that contains) إصدار (the HTTP version) HTTP المستخدم (used) في الاستجابة (in the response)، ورمز حالة (a numeric status code) رقمي (numeric) يلخص (that summarizes) نتيجة (the result of) الطلب (the request)، وعبارة سبب (and a reason phrase) توفر (that provides) وصفًا نصيًا (a text description) لرمز الحالة (of the status code). بعد (after) تسلسل (the CRLF sequence) CRLF توجد (are) أي رؤوس (any headers)، وتسلسل (another CRLF sequence) CRLF آخر (another)، وجسم (and the body) الاستجابة (of the response).

فيما يلي (here is) مثال (an example) على (of) استجابة (a response) تستخدم (that uses) إصدار (HTTP version) HTTP 1.1 ولها (and has) رمز حالة (a status code of) 200، وعبارة سبب (an OK reason phrase) OK، وبدون (no) رؤوس (headers)، وبدون (and no) جسم (body):

```text
HTTP/1.1 200 OK\r\n\r\n
```

رمز الحالة (status code) 200 هو (is) استجابة النجاح القياسية (the standard success response). النص (the text) هو (is) استجابة (a tiny successful HTTP response) HTTP ناجحة (successful) صغيرة (tiny). لنكتب (let's write) هذا (this) إلى التدفق (to the stream) كاستجابتنا (as our response) لطلب (for a successful request) ناجح (successful)! من (from) دالة (the function) `handle_connection`، احذف (remove) `println!` التي كانت (that was) تطبع (printing) بيانات الطلب (the request data) واستبدلها (and replace it) بالكود (with the code) في القائمة (in Listing) 21-3.

<Listing number="21-3" file-name="src/main.rs" caption="كتابة (writing) استجابة (a tiny successful HTTP response) HTTP ناجحة (successful) صغيرة (tiny) إلى التدفق (to the stream)">

```rust,no_run
{{#rustdoc_include ../listings/ch21-web-server/listing-21-03/src/main.rs:here}}
```

</Listing>

يحدد (defines) السطر الجديد الأول (the first new line) متغير (the variable) `response` الذي يحمل (that holds) بيانات (the data of) رسالة النجاح (the success message). ثم (then) نستدعي (we call) `as_bytes` على (on) `response` لتحويل (to convert) بيانات السلسلة (the string data) إلى (to) بايتات (bytes). تأخذ (takes) طريقة (the method) `write_all` على (on) `stream` مرجعًا (a reference) `&[u8]` وترسل (and sends) تلك البايتات (those bytes) مباشرة (directly) عبر الاتصال (down the connection). نظرًا لأن (because) عملية (the operation) `write_all` يمكن (can) أن تفشل (fail)، نستخدم (we use) `unwrap` على (on) أي نتيجة خطأ (any error result) كما كان (as) من قبل (before). مرة أخرى (again)، في (in) تطبيق حقيقي (a real application)، ستضيف (you would add) معالجة الأخطاء (error handling) هنا (here).

مع (with) هذه التغييرات (these changes)، لنشغل (let's run) كودنا (our code) ونقدم (and make) طلبًا (a request). لم نعد (we're no longer) نطبع (printing) أي بيانات (any data) إلى الطرفية (to the terminal)، لذلك (so) لن نرى (we won't see) أي إخراج (any output) غير (other than) الإخراج (the output) من (from) Cargo. عندما (when) تحمّل (you load) _127.0.0.1:7878_ في (in) متصفح الويب (a web browser)، يجب (should) أن تحصل على (get) صفحة فارغة (a blank page) بدلاً من (instead of) خطأ (an error). لقد (you've just) قمت (handcoded) للتو (just) بكتابة يدوية (handcoding) لاستقبال (receiving) طلب (an HTTP request) HTTP وإرسال (and sending) استجابة (a response)!

### إرجاع HTML حقيقي (Returning Real HTML)

لننفذ (let's implement) الوظيفة (the functionality) لإرجاع (for returning) أكثر من (more than) صفحة فارغة (a blank page). أنشئ (create) الملف الجديد (the new file) _hello.html_ في (in) جذر (the root of) دليل مشروعك (your project directory)، وليس (not) في (in) دليل (the directory) _src_. يمكنك (you can) إدخال (input) أي (any) HTML تريده (you want)؛ تعرض (shows) القائمة (Listing) 21-4 إمكانية واحدة (one possibility).

<Listing number="21-4" file-name="hello.html" caption="ملف (a sample HTML file) HTML نموذجي (sample) لإرجاعه (to return) في استجابة (in a response)">

```html
{{#include ../listings/ch21-web-server/listing-21-05/hello.html}}
```

</Listing>

هذه (this is) وثيقة (a document) HTML5 بسيطة (minimal) بعنوان (with a heading) وبعض النص (and some text). لإرجاع (to return) هذا (this) من الخادوم (from the server) عند (when) استقبال (receiving) طلب (a request)، سنعدل (we'll modify) `handle_connection` كما هو موضح (as shown) في القائمة (in Listing) 21-5 لقراءة (to read) ملف (the HTML file) HTML، وإضافته (add it) إلى الاستجابة (to the response) كجسم (as a body)، وإرساله (and send it).

<Listing number="21-5" file-name="src/main.rs" caption="إرسال (sending) محتويات (the contents of) *hello.html* كجسم (as the body) للاستجابة (of the response)">

```rust,no_run
{{#rustdoc_include ../listings/ch21-web-server/listing-21-05/src/main.rs:here}}
```

</Listing>

أضفنا (we've added) `fs` إلى (to) عبارة (the use statement) `use` لجلب (to bring) وحدة (the module) نظام الملفات (the filesystem) الخاصة بالمكتبة القياسية (of the standard library) إلى النطاق (into scope). يجب (should) أن يبدو (look) الكود (the code) لقراءة (for reading) محتويات الملف (the contents of a file) إلى سلسلة (into a string) مألوفًا (familiar)؛ استخدمناه (we used it) عندما (when) قرأنا (we read) محتويات (the contents of) ملف (a file) لمشروع (for our I/O project) I/O الخاص بنا (our) في القائمة (in Listing) 12-4.

بعد ذلك (next)، نستخدم (we use) `format!` لإضافة (to add) محتويات الملف (the file's contents) كجسم (as the body) لاستجابة النجاح (of the success response). لضمان (to ensure) استجابة (a valid HTTP response) HTTP صالحة (valid)، نضيف (we add) رأس (the Content-Length header) `Content-Length`، والذي (which) يتم تعيينه (is set) على (to) حجم (the size of) جسم (the body of) استجابتنا (our response)—في هذه الحالة (in this case)، حجم (the size of) `hello.html`.

شغّل (run) هذا الكود (this code) مع (with) `cargo run` وحمّل (and load) _127.0.0.1:7878_ في متصفحك (in your browser)؛ يجب (should) أن ترى (see) HTML الخاص بك (your HTML) معروضًا (rendered)!

حاليًا (currently)، نحن (we're) نتجاهل (ignoring) بيانات الطلب (the request data) في (in) `http_request` ونرسل (and just sending) فقط (just) محتويات (the contents of) ملف (the HTML file) HTML بشكل غير مشروط (unconditionally). وهذا يعني (that means) أنه (that) إذا (if) حاولت (you try) طلب (requesting) _127.0.0.1:7878/something-else_ في متصفحك (in your browser)، فستظل (you'll still) تحصل على (get) نفس (the same) استجابة (HTML response) HTML هذه (this). في الوقت الحالي (at the moment)، خادومنا (our server) محدود جدًا (is very limited) ولا يقوم بما (and isn't doing what) تفعله (do) معظم (most) خوادم الويب (web servers). نريد (we want) تخصيص (to customize) استجاباتنا (our responses) حسب الطلب (based on the request) وإرسال (and only send back) ملف (the HTML file) HTML فقط (only) لطلب (for a well-formed request) صحيح (well-formed) إلى (for) _/_.

### التحقق من الطلب والاستجابة بشكل انتقائي (Validating the Request and Selectively Responding)

الآن (right now)، سيُرجع (will return) خادوم الويب (our web server) الخاص بنا (our) HTML في الملف (the HTML in the file) بغض النظر (no matter) عما (what) طلبه (requested) العميل (the client). لنضف (let's add) الوظيفة (functionality) للتحقق من (to check) أن (that) المتصفح (the browser) يطلب (is requesting) _/_ قبل (before) إرجاع (returning) ملف (the HTML file) HTML وإرجاع (and return) خطأ (an error) إذا (if) طلب (requests) المتصفح (the browser) أي شيء آخر (anything else). لهذا (for this) نحتاج (we need) إلى تعديل (to modify) `handle_connection`، كما هو موضح (as shown) في القائمة (in Listing) 21-6. يتحقق (checks) هذا الكود الجديد (this new code) من (the) محتوى (content of) الطلب المستلم (the request received) مقابل (against) ما (what) نعرفه (we know) عن (about what) شكل (looks like) طلب (a request) لـ (for) _/_ ويضيف (and adds) كتل (if and else blocks) `if` و (and) `else` لمعاملة (to treat) الطلبات (requests) بشكل مختلف (differently).

<Listing number="21-6" file-name="src/main.rs" caption="معالجة (handling) الطلبات (requests) إلى (to) */* بشكل مختلف (differently) عن (from) الطلبات الأخرى (other requests)">

```rust,no_run
{{#rustdoc_include ../listings/ch21-web-server/listing-21-06/src/main.rs:here}}
```

</Listing>

سننظر (we're only going to look) فقط (only) إلى (at) السطر الأول (the first line) من (of) طلب (the HTTP request) HTTP، لذا (so) بدلاً من (rather than) قراءة (reading) الطلب (the request) بالكامل (entirely) في (into) متجه (a vector)، نستدعي (we're calling) `next` للحصول على (to get) العنصر الأول (the first item) من المكرر (from the iterator). يعتني (takes care of) أول (the first) `unwrap` بـ (the) `Option` ويوقف (and stops) البرنامج (the program) إذا (if) لم يكن للمكرر (the iterator has) أي عناصر (no items). يتعامل (handles) `unwrap` الثاني (the second) مع (the) `Result` وله (and has) نفس التأثير (the same effect) مثل (as) `unwrap` الذي كان (that was) في (in) `map` المضاف (added) في القائمة (in Listing) 21-2.

بعد ذلك (next)، نتحقق من (we check) `request_line` لنرى (to see) ما إذا كان (whether it) يساوي (equals) سطر الطلب (the request line) لطلب (of a GET request) GET إلى (to) مسار (the path) _/_. إذا (if) كان الأمر كذلك (it does)، تُرجع (returns) كتلة (the if block) `if` محتويات (the contents of) ملف (our HTML file) HTML الخاص بنا (our).

إذا (if) لم يساوِ (doesn't equal) `request_line` طلب (the GET request) GET إلى (to) مسار (the path) _/_، فهذا يعني (it means) أننا (that we've) تلقينا (received) طلبًا (some other request) آخر (other). سنضيف (we'll add) كودًا (code) إلى (to) كتلة (the else block) `else` في لحظة (in a moment) للاستجابة (to respond) لجميع (to all) الطلبات (other requests) الأخرى (other).

شغّل (run) هذا الكود (this code) الآن (now) واطلب (and request) _127.0.0.1:7878_؛ يجب (should) أن تحصل على (get) HTML في (the HTML in) _hello.html_. إذا (if) قدمت (you make) أي طلب (any other request) آخر (other)، مثل (such as) _127.0.0.1:7878/something-else_، فستحصل على (you'll get) خطأ اتصال (a connection error) مثل (like) تلك التي (the ones) رأيتها (you saw) عند تشغيل (when running) الكود (the code) في القائمة (in Listing) 21-1 والقائمة (and Listing) 21-2.

الآن (now) لنضف (let's add) الكود (the code) في القائمة (in Listing) 21-7 إلى (to) كتلة (the else block) `else` لإرجاع (to return) استجابة (a response) برمز حالة (with status code) 404، الذي (which) يشير إلى (signals) عدم العثور على (that the content for) المحتوى (the content) للطلب (the request) لم يتم العثور عليه (was not found). سنُرجع (we'll also return) أيضًا (also) بعض (some) HTML لصفحة (for a page) لعرضها (to render) في المتصفح (in the browser) لتشير إلى (to indicate) الاستجابة (the response) للمستخدم النهائي (to the end user).

<Listing number="21-7" file-name="src/main.rs" caption="الاستجابة (responding) برمز الحالة (with status code) 404 وصفحة خطأ (and an error page) إذا (if) تم طلب (was requested) أي شيء (anything) غير (other than) */*">

```rust,no_run
{{#rustdoc_include ../listings/ch21-web-server/listing-21-07/src/main.rs:here}}
```

</Listing>

هنا (here)، استجابتنا (our response) لها (has) سطر حالة (a status line) برمز حالة (with status code) 404 وعبارة السبب (and the reason phrase) `NOT FOUND`. سيكون (will be) جسم (the body of) الاستجابة (the response) هو (the) HTML في الملف (in the file) _404.html_. ستحتاج (you'll need) إلى إنشاء (to create) ملف (a file) _404.html_ بجوار (next to) _hello.html_ لصفحة الخطأ (for the error page)؛ مرة أخرى (again)، لا تتردد في (feel free to) استخدام (use) أي (any) HTML تريده (you like)، أو (or) استخدم (use) مثال (the sample) HTML في القائمة (in Listing) 21-8.

<Listing number="21-8" file-name="404.html" caption="محتوى نموذجي (sample content) للصفحة (for the page) لإرسالها (to send) مع (with) أي استجابة (any 404 response) 404">

```html
{{#include ../listings/ch21-web-server/listing-21-07/404.html}}
```

</Listing>

مع (with) هذه التغييرات (these changes)، شغّل (run) خادومك (your server) مرة أخرى (again). طلب (requesting) _127.0.0.1:7878_ يجب (should) أن يُرجع (return) محتويات (the contents of) _hello.html_، وأي طلب (and any other request) آخر (other)، مثل (such as) _127.0.0.1:7878/foo_، يجب (should) أن يُرجع (return) خطأ (the error) HTML من (HTML from) _404.html_.

<!-- Old headings. Do not remove or links may break. -->

<a id="a-touch-of-refactoring"></a>

### إعادة الهيكلة (A Touch of Refactoring)

في الوقت الحالي (at the moment)، كتل (the if and else blocks) `if` و (and) `else` لديها (have) الكثير (a lot of) من التكرار (repetition): كلاهما (both of them are) يقرأ (reading) الملفات (files) ويكتب (and writing) محتويات الملفات (the contents of the files) إلى التدفق (to the stream). الاختلافات الوحيدة (the only differences) هي (are) سطر الحالة (the status line) واسم الملف (and the filename). لنجعل (let's make) الكود (the code) أكثر إيجازًا (more concise) عن طريق (by) استخراج (pulling out) هذه الاختلافات (those differences) في (into) أسطر (separate if and else lines) `if` و (and) `else` منفصلة (separate) ستعيّن (that will assign) قيم (the values of) سطر الحالة (the status line) واسم الملف (and the filename) إلى المتغيرات (to variables)؛ يمكننا (we can) بعد ذلك (then) استخدام (use) تلك المتغيرات (those variables) بشكل غير مشروط (unconditionally) في الكود (in the code) لقراءة (to read) الملف (the file) وكتابة (and write) الاستجابة (the response). تُظهر (shows) القائمة (Listing) 21-9 الكود الناتج (the resulting code) بعد (after) استبدال (replacing) كتل (the large if and else blocks) `if` و (and) `else` الكبيرة (large).

<Listing number="21-9" file-name="src/main.rs" caption="إعادة هيكلة (refactoring) كتل (the if and else blocks) `if` و (and) `else` لتحتوي (to contain) فقط (only) على الكود (the code) الذي يختلف (that differs) بين الحالتين (between the two cases)">

```rust,no_run
{{#rustdoc_include ../listings/ch21-web-server/listing-21-09/src/main.rs:here}}
```

</Listing>

الآن (now) تُرجع (return) كتل (the if and else blocks) `if` و (and) `else` فقط (only) القيم المناسبة (the appropriate values) لسطر الحالة (for the status line) واسم الملف (and the filename) في (in) صفة (a tuple)؛ ثم (then) نستخدم (we use) destructuring لتعيين (to assign) هاتين القيمتين (these two values) إلى (to) `status_line` و (and) `filename` باستخدام (using) نمط (a pattern) في (in) عبارة (the let statement) `let`، كما تمت مناقشته (as discussed) في الفصل (in Chapter) 19.

الكود المكرر (the previously duplicated code) سابقًا (previously) الآن (is now) خارج (outside) كتل (the if and else blocks) `if` و (and) `else` ويستخدم (and uses) متغيرات (the variables) `status_line` و (and) `filename`. هذا (this) يجعل (makes it) من الأسهل (easier) رؤية (to see) الفرق (the difference) بين الحالتين (between the two cases)، ويعني (and it means) أن (that) لدينا (we have) مكانًا واحدًا (only one place) فقط (only) لتحديث (to update) الكود (the code) إذا (if) أردنا (we want) تغيير (to change) كيفية عمل (how) قراءة الملف (the file reading) وكتابة الاستجابة (and response writing) (work). سيكون (will be) سلوك (the behavior of) الكود (the code) في القائمة (in Listing) 21-9 هو نفسه (the same) كما (as that) في القائمة (in Listing) 21-7.

رائع (awesome)! الآن (now) لدينا (we have) خادوم ويب (a simple web server) بسيط (simple) في حوالي (in about) 40 سطرًا (40 lines) من (of) كود (Rust code) Rust يستجيب (that responds) لطلب (to one request) واحد (one) بصفحة محتوى (with a page of content) ويستجيب (and responds) لجميع (to all) الطلبات (other requests) الأخرى (other) باستجابة (with a 404 response) 404.

حاليًا (currently)، يعمل (runs) خادومنا (our server) في (in) خيط واحد (a single thread)، مما يعني (meaning) أنه (it) يمكنه (can) خدمة (serve) طلب (only one request) واحد (one) فقط (only) في كل مرة (at a time). لنفحص (let's examine) كيف (how) يمكن (can be) أن تكون (that can be) هذه (this) مشكلة (a problem) عن طريق (by) محاكاة (simulating) بعض (some) الطلبات البطيئة (slow requests). ثم (then) سنصلحها (we'll fix it) حتى (so) يتمكن (can) خادومنا (our server) من معالجة (handle) طلبات متعددة (multiple requests) في وقت واحد (at once).
