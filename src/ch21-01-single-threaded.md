## بناء خادوم ويب أحادي الخيط (Building a Single-Threaded Web Server)

سنبدأ بتشغيل خادوم ويب (web server) أحادي الخيط (single-threaded). قبل أن نبدأ، دعونا نلقي نظرة سريعة على البروتوكولات (protocols) المستخدمة في بناء خوادم الويب (web servers). تفاصيل هذه البروتوكولات خارج نطاق هذا الكتاب، ولكن نظرة عامة موجزة ستعطيك المعلومات التي تحتاجها.

البروتوكولان الرئيسيان المستخدمان في خوادم الويب (web servers) هما _Hypertext Transfer Protocol_ _(HTTP)_ و _Transmission Control Protocol_ _(TCP)_. كلا البروتوكولين (protocols) هما بروتوكولا _request-response_ طلب-استجابة (request-response)، مما يعني أن _client_ (عميل) (client) يبدأ الطلبات (requests) و _server_ (خادوم) (server) يستمع للطلبات ويوفر استجابة (response) للعميل (client). محتويات تلك الطلبات والاستجابات (responses) محددة بواسطة البروتوكولات.

TCP هو البروتوكول (protocol) ذو المستوى الأدنى (lower-level) الذي يصف تفاصيل كيفية انتقال المعلومات من خادوم (server) إلى آخر ولكنه لا يحدد ما هي تلك المعلومات. يبني HTTP على TCP من خلال تحديد محتويات الطلبات (requests) والاستجابات (responses). من الممكن تقنيًا استخدام HTTP مع بروتوكولات (protocols) أخرى، ولكن في الغالبية العظمى من الحالات، يرسل HTTP بياناته عبر TCP. سنعمل مع البايتات (bytes) الخام لطلبات واستجابات TCP و HTTP.

### الاستماع لاتصال TCP (Listening to the TCP Connection)

يحتاج خادوم الويب (web server) الخاص بنا إلى الاستماع لاتصال (connection) TCP، لذا فهذا هو الجزء الأول الذي سنعمل عليه. توفر المكتبة القياسية (standard library) وحدة (module) `std::net` تتيح لنا القيام بذلك. لنصنع مشروعًا جديدًا بالطريقة المعتادة:

```console
$ cargo new hello
     Created binary (application) `hello` project
$ cd hello
```

الآن أدخل الكود (code) في القائمة (Listing) 21-1 في _src/main.rs_ للبدء. سيستمع هذا الكود عند العنوان المحلي (local address) `127.0.0.1:7878` للتدفقات (streams) الواردة TCP. عندما يحصل على تدفق (stream) وارد، سيطبع `Connection established!`.

<Listing number="21-1" file-name="src/main.rs" caption="الاستماع للتدفقات (streams) الواردة وطباعة رسالة عندما نستقبل تدفقًا (stream)">

```rust,no_run
{{#rustdoc_include ../listings/ch21-web-server/listing-21-01/src/main.rs}}
```

</Listing>

باستخدام `TcpListener`، يمكننا الاستماع لاتصالات (connections) TCP على العنوان (address) `127.0.0.1:7878`. في العنوان، القسم قبل النقطتين هو عنوان (IP address) IP يمثل جهاز الكمبيوتر الخاص بك (هذا هو نفسه على كل جهاز كمبيوتر ولا يمثل كمبيوتر المؤلفين بشكل خاص)، و `7878` هو المنفذ (port). اخترنا هذا المنفذ لسببين: لا يتم قبول HTTP عادة على هذا المنفذ، لذا فإن خادومنا (server) من غير المحتمل أن يتعارض مع أي خادوم ويب (web server) آخر قد يكون لديك قيد التشغيل على جهازك، و 7878 هو _rust_ مكتوبة على الهاتف.

تعمل دالة (function) `bind` في هذا السيناريو (scenario) مثل دالة `new` من حيث أنها ستُرجع نسخة (instance) جديدة من `TcpListener`. تُسمى الدالة `bind` لأنه، في الشبكات (networking)، الاتصال بمنفذ (port) للاستماع يُعرف باسم "binding to a port" (ربط بمنفذ) (binding to a port).

تُرجع دالة (function) `bind` نتيجة `Result<T, E>`، مما يشير إلى أنه من الممكن أن يفشل الربط (binding)، على سبيل المثال، إذا قمنا بتشغيل نسختين (instances) من برنامجنا وبالتالي كان لدينا برنامجان يستمعان إلى نفس المنفذ (port). نظرًا لأننا نكتب خادومًا (server) أساسيًا فقط لأغراض التعلم، فلن نقلق بشأن معالجة هذه الأنواع من الأخطاء؛ بدلاً من ذلك، نستخدم `unwrap` لإيقاف البرنامج إذا حدثت أخطاء.

تُرجع الطريقة (method) `incoming` على `TcpListener` مُكرِّرًا (iterator) يعطينا تسلسلاً من التدفقات (streams) (بشكل أكثر تحديدًا، تدفقات من نوع `TcpStream`). _stream_ (تدفق) (stream) واحد يمثل اتصالاً (connection) مفتوحًا بين العميل (client) والخادوم (server). _Connection_ (اتصال) (connection) هو الاسم لعملية الطلب (request) والاستجابة (response) الكاملة التي يتصل فيها العميل بالخادوم، ويولد الخادوم استجابة، ويغلق الخادوم الاتصال. على هذا النحو، سنقرأ من `TcpStream` لنرى ما أرسله العميل ثم نكتب استجابتنا إلى التدفق (stream) لإرسال البيانات (data) مرة أخرى إلى العميل. بشكل عام، ستعالج حلقة `for` هذه كل اتصال بدوره وتنتج سلسلة من التدفقات لنتعامل معها.

في الوقت الحالي، تتكون معالجتنا للتدفق (stream) من استدعاء `unwrap` لإنهاء برنامجنا إذا كان للتدفق أي أخطاء؛ إذا لم تكن هناك أخطاء، يطبع البرنامج رسالة. سنضيف المزيد من الوظائف (functionality) لحالة النجاح في القائمة (listing) التالية. السبب في أننا قد نتلقى أخطاء من طريقة (method) `incoming` عندما يتصل عميل (client) بالخادوم (server) هو أننا لا نكرر فعليًا على الاتصالات (connections). بدلاً من ذلك، نكرر على _محاولات اتصال_ (connection attempts). قد لا يكون الاتصال (connection) ناجحًا لعدة أسباب، الكثير منها خاص بنظام التشغيل (operating system). على سبيل المثال، للعديد من أنظمة التشغيل (operating systems) حد لعدد الاتصالات المفتوحة المتزامنة التي يمكنها دعمها؛ ستنتج محاولات الاتصال الجديدة التي تتجاوز هذا العدد خطأ حتى يتم إغلاق بعض الاتصالات المفتوحة.

لنحاول تشغيل هذا الكود (code)! استدعِ `cargo run` في الطرفية (terminal)، ثم قم بتحميل _127.0.0.1:7878_ في متصفح الويب (web browser). يجب أن يعرض المتصفح (browser) رسالة خطأ مثل "Connection reset" لأن الخادوم (server) لا يرسل حاليًا أي بيانات (data). ولكن عندما تنظر إلى طرفيتك، يجب أن ترى عدة رسائل تمت طباعتها عندما اتصل المتصفح بالخادوم!

```text
     Running `target/debug/hello`
Connection established!
Connection established!
Connection established!
```

في بعض الأحيان سترى رسائل متعددة مطبوعة لطلب (request) متصفح (browser) واحد؛ قد يكون السبب هو أن المتصفح يقدم طلبًا للصفحة بالإضافة إلى طلب لموارد أخرى، مثل أيقونة _favicon.ico_ التي تظهر في علامة تبويب (tab) المتصفح.

قد يكون أيضًا أن المتصفح (browser) يحاول الاتصال بالخادوم (server) عدة مرات لأن الخادوم لا يستجيب بأي بيانات (data). عندما يخرج `stream` من النطاق (scope) ويتم إسقاطه في نهاية الحلقة (loop)، يتم إغلاق الاتصال (connection) كجزء من تطبيق (implementation) `drop`. تتعامل المتصفحات (browsers) أحيانًا مع الاتصالات (connections) المغلقة عن طريق إعادة المحاولة، لأن المشكلة قد تكون مؤقتة.

تفتح المتصفحات (browsers) أيضًا في بعض الأحيان اتصالات (connections) متعددة بالخادوم (server) دون إرسال أي طلبات (requests) بحيث إذا أرسلت طلبات لاحقًا، يمكن أن تحدث هذه الطلبات بشكل أسرع. عندما يحدث هذا، سيرى خادومنا كل اتصال (connection)، بغض النظر عما إذا كانت هناك أي طلبات عبر ذلك الاتصال. تقوم العديد من إصدارات (versions) المتصفحات المستندة إلى Chrome بذلك، على سبيل المثال؛ يمكنك تعطيل هذا التحسين (optimization) باستخدام وضع التصفح الخاص أو استخدام متصفح (browser) مختلف.

العامل المهم هو أننا نجحنا في الحصول على مقبض (handle) لاتصال (connection) TCP!

تذكر إيقاف البرنامج بالضغط على <kbd>ctrl</kbd>-<kbd>C</kbd> عندما تنتهي من تشغيل إصدار معين من الكود (code). ثم أعد تشغيل البرنامج عن طريق استدعاء أمر (command) `cargo run` بعد إجراء كل مجموعة من تغييرات الكود للتأكد من أنك تشغل أحدث كود.

### قراءة الطلب (Reading the Request)

لنطبق الوظيفة (functionality) لقراءة الطلب (request) من المتصفح (browser)! لفصل المهام المتمثلة في الحصول أولاً على اتصال (connection) ثم اتخاذ بعض الإجراءات مع الاتصال، سنبدأ دالة (function) جديدة لمعالجة الاتصالات (connections). في دالة `handle_connection` الجديدة هذه، سنقرأ البيانات (data) من تدفق (stream) TCP ونطبعها حتى نتمكن من رؤية البيانات المرسلة من المتصفح. غيّر الكود (code) ليبدو مثل القائمة (Listing) 21-2.

<Listing number="21-2" file-name="src/main.rs" caption="القراءة من `TcpStream` وطباعة البيانات (data)">

```rust,no_run
{{#rustdoc_include ../listings/ch21-web-server/listing-21-02/src/main.rs}}
```

</Listing>

نجلب `std::io::BufReader` و `std::io::prelude` إلى النطاق (scope) للوصول إلى السمات (traits) والأنواع (types) التي تتيح لنا القراءة من والكتابة إلى التدفق (stream). في حلقة (loop) `for` في دالة (function) `main`، بدلاً من طباعة رسالة تقول إننا أنشأنا اتصالاً (connection)، نستدعي الآن دالة `handle_connection` الجديدة ونمرر `stream` إليها.

في دالة (function) `handle_connection`، نُنشئ نسخة (instance) جديدة من `BufReader` تلتف حول مرجع (reference) إلى `stream`. يضيف `BufReader` التخزين المؤقت (buffering) عن طريق إدارة الاستدعاءات لطرق (methods) سمة (trait) `std::io::Read` لنا.

نُنشئ متغيرًا (variable) باسم `http_request` لجمع أسطر الطلب (request) التي يرسلها المتصفح (browser) إلى خادومنا (server). نشير إلى أننا نريد جمع هذه الأسطر في متجه (vector) عن طريق إضافة توضيح النوع (type annotation) `Vec<_>`.

يطبق `BufReader` سمة (trait) `std::io::BufRead`، والتي توفر طريقة (method) `lines`. تُرجع طريقة `lines` مُكرِّرًا (iterator) لـ `Result<String, std::io::Error>` عن طريق تقسيم تدفق (stream) البيانات (data) كلما رأى بايت (byte) سطر جديد. للحصول على كل `String`، نستخدم `map` و `unwrap` لكل `Result`. قد يكون `Result` خطأً إذا لم تكن البيانات UTF-8 صالحة أو إذا كانت هناك مشكلة في القراءة من التدفق. مرة أخرى، يجب على البرنامج الإنتاجي معالجة هذه الأخطاء بشكل أكثر رشاقة، لكننا نختار إيقاف البرنامج في حالة الخطأ من أجل البساطة.

يشير المتصفح (browser) إلى نهاية طلب (request) HTTP عن طريق إرسال حرفي سطر جديد متتاليين، لذلك للحصول على طلب واحد من التدفق (stream)، نأخذ الأسطر حتى نحصل على سطر فارغ. بمجرد جمع الأسطر في المتجه (vector)، نطبعها باستخدام تنسيق التصحيح (debug formatting) الجميل حتى نتمكن من إلقاء نظرة على التعليمات التي يرسلها متصفح الويب (web browser) إلى خادومنا (server).

لنجرب هذا الكود (code)! ابدأ البرنامج واطلب (request) في متصفح الويب (web browser) مرة أخرى. لاحظ أننا سنظل نحصل على صفحة خطأ في المتصفح (browser)، لكن إخراج برنامجنا في الطرفية (terminal) سيبدو الآن مشابهًا لهذا:

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

اعتمادًا على متصفحك (browser)، قد تحصل على إخراج (output) مختلف قليلاً. الآن بعد أن نطبع بيانات (data) الطلب (request)، يمكننا معرفة سبب حصولنا على اتصالات (connections) متعددة من طلب متصفح واحد من خلال النظر إلى المسار (path) بعد `GET` في السطر الأول من الطلب. إذا كانت الاتصالات المتكررة تطلب جميعها _/_، فنحن نعلم أن المتصفح يحاول جلب _/_ بشكل متكرر لأنه لا يحصل على استجابة (response) من برنامجنا.

لنحلل بيانات (data) الطلب (request) هذه لفهم ما يطلبه المتصفح (browser) من برنامجنا.

<!-- Old headings. Do not remove or links may break. -->

<a id="a-closer-look-at-an-http-request"></a>
<a id="looking-closer-at-an-http-request"></a>

### نظرة أقرب على طلب HTTP (A Closer Look at an HTTP Request)

HTTP هو بروتوكول (protocol) نصي، والطلب (request) يأخذ هذا التنسيق (format):

```text
Method Request-URI HTTP-Version CRLF
headers CRLF
message-body
```

السطر الأول هو _request line_ (سطر الطلب) (request line) الذي يحمل معلومات حول ما يطلبه العميل (client). يشير الجزء الأول من سطر الطلب (request line) إلى الطريقة (method) المستخدمة، مثل `GET` أو `POST`، والتي تصف كيف يقدم العميل هذا الطلب (request). استخدم عميلنا طلب `GET`، مما يعني أنه يطلب معلومات.

الجزء التالي من سطر الطلب (request line) هو _/_، والذي يشير إلى _uniform resource identifier_ _(URI)_ (معرّف الموارد الموحد) (URI) الذي يطلبه العميل (client): URI يكاد يكون، ولكن ليس تمامًا، مثل _uniform resource locator_ _(URL)_ (محدد موقع الموارد الموحد) (URL). الفرق بين URIs و URLs ليس مهمًا لأغراضنا في هذا الفصل، ولكن مواصفات (specification) HTTP تستخدم مصطلح (term) _URI_، لذا يمكننا فقط استبدال _URL_ ذهنيًا بـ _URI_ هنا.

الجزء الأخير هو إصدار (version) HTTP الذي يستخدمه العميل (client)، ثم ينتهي سطر الطلب (request line) بتسلسل (sequence) CRLF. (_CRLF_ تعني _carriage return_ و _line feed_، وهي مصطلحات من أيام الآلة الكاتبة!) يمكن أيضًا كتابة تسلسل CRLF على شكل `\r\n`، حيث `\r` هو carriage return و `\n` هو line feed. يفصل _CRLF sequence_ (تسلسل CRLF) (CRLF sequence) سطر الطلب عن بقية بيانات (data) الطلب (request). لاحظ أنه عندما يتم طباعة CRLF، نرى بداية سطر جديد بدلاً من `\r\n`.

بالنظر إلى بيانات (data) سطر الطلب (request line) التي تلقيناها من تشغيل برنامجنا حتى الآن، نرى أن `GET` هو الطريقة (method)، _/_ هو URI الطلب (request URI)، و `HTTP/1.1` هو الإصدار (version).

بعد سطر الطلب (request line)، الأسطر المتبقية بدءًا من `Host:` فصاعدًا هي الرؤوس (headers). طلبات (requests) `GET` ليس لها جسم (body).

حاول تقديم طلب (request) من متصفح (browser) مختلف أو طلب عنوان (address) مختلف، مثل _127.0.0.1:7878/test_، لترى كيف تتغير بيانات (data) الطلب.

الآن بعد أن عرفنا ما يطلبه المتصفح (browser)، لنرسل بعض البيانات (data)!

### كتابة استجابة (Writing a Response)

سنطبق إرسال البيانات (data) في استجابة (response) لطلب (request) العميل (client). الاستجابات (responses) لها التنسيق (format) التالي:

```text
HTTP-Version Status-Code Reason-Phrase CRLF
headers CRLF
message-body
```

السطر الأول هو _status line_ (سطر الحالة) (status line) الذي يحتوي على إصدار (version) HTTP المستخدم في الاستجابة (response)، ورمز حالة (status code) رقمي يلخص نتيجة الطلب (request)، وعبارة سبب (reason phrase) توفر وصفًا نصيًا لرمز الحالة. بعد تسلسل (sequence) CRLF توجد أي رؤوس (headers)، وتسلسل CRLF آخر، وجسم (body) الاستجابة.

فيما يلي مثال على استجابة (response) تستخدم إصدار (version) HTTP 1.1 ولها رمز حالة (status code) 200، وعبارة سبب (reason phrase) OK، وبدون رؤوس (headers)، وبدون جسم (body):

```text
HTTP/1.1 200 OK\r\n\r\n
```

رمز الحالة (status code) 200 هو استجابة (response) النجاح القياسية. النص هو استجابة HTTP ناجحة صغيرة. لنكتب هذا إلى التدفق (stream) كاستجابتنا لطلب (request) ناجح! من دالة (function) `handle_connection`، احذف `println!` التي كانت تطبع بيانات (data) الطلب واستبدلها بالكود (code) في القائمة (Listing) 21-3.

<Listing number="21-3" file-name="src/main.rs" caption="كتابة استجابة (response) HTTP ناجحة صغيرة إلى التدفق (stream)">

```rust,no_run
{{#rustdoc_include ../listings/ch21-web-server/listing-21-03/src/main.rs:here}}
```

</Listing>

يحدد السطر الجديد الأول متغير (variable) `response` الذي يحمل بيانات (data) رسالة النجاح. ثم نستدعي `as_bytes` على `response` لتحويل بيانات السلسلة إلى بايتات (bytes). تأخذ طريقة (method) `write_all` على `stream` مرجعًا (reference) `&[u8]` وترسل تلك البايتات مباشرة عبر الاتصال (connection). نظرًا لأن عملية (operation) `write_all` يمكن أن تفشل، نستخدم `unwrap` على أي نتيجة خطأ كما كان من قبل. مرة أخرى، في تطبيق (application) حقيقي، ستضيف معالجة الأخطاء هنا.

مع هذه التغييرات، لنشغل كودنا (code) ونقدم طلبًا (request). لم نعد نطبع أي بيانات (data) إلى الطرفية (terminal)، لذلك لن نرى أي إخراج (output) غير الإخراج من Cargo. عندما تحمّل _127.0.0.1:7878_ في متصفح الويب (web browser)، يجب أن تحصل على صفحة فارغة بدلاً من خطأ. لقد قمت للتو بكتابة يدوية لاستقبال طلب HTTP وإرسال استجابة (response)!

### إرجاع HTML حقيقي (Returning Real HTML)

لننفذ الوظيفة (functionality) لإرجاع أكثر من صفحة فارغة. أنشئ الملف (file) الجديد _hello.html_ في جذر دليل مشروعك، وليس في دليل (directory) _src_. يمكنك إدخال أي HTML تريده؛ تعرض القائمة (Listing) 21-4 إمكانية واحدة.

<Listing number="21-4" file-name="hello.html" caption="ملف (file) HTML نموذجي لإرجاعه في استجابة (response)">

```html
{{#include ../listings/ch21-web-server/listing-21-05/hello.html}}
```

</Listing>

هذه وثيقة (document) HTML5 بسيطة بعنوان وبعض النص. لإرجاع هذا من الخادوم (server) عند استقبال طلب (request)، سنعدل `handle_connection` كما هو موضح في القائمة (Listing) 21-5 لقراءة ملف (file) HTML، وإضافته إلى الاستجابة (response) كجسم (body)، وإرساله.

<Listing number="21-5" file-name="src/main.rs" caption="إرسال محتويات *hello.html* كجسم (body) للاستجابة (response)">

```rust,no_run
{{#rustdoc_include ../listings/ch21-web-server/listing-21-05/src/main.rs:here}}
```

</Listing>

أضفنا `fs` إلى عبارة (statement) `use` لجلب وحدة (module) نظام الملفات (filesystem) الخاصة بالمكتبة القياسية (standard library) إلى النطاق (scope). يجب أن يبدو الكود (code) لقراءة محتويات الملف (file) إلى سلسلة مألوفًا؛ استخدمناه عندما قرأنا محتويات ملف لمشروع I/O الخاص بنا في القائمة (Listing) 12-4.

بعد ذلك، نستخدم `format!` لإضافة محتويات الملف (file) كجسم (body) لاستجابة (response) النجاح. لضمان استجابة HTTP صالحة، نضيف رأس (header) `Content-Length`، والذي يتم تعيينه على حجم جسم استجابتنا—في هذه الحالة، حجم `hello.html`.

شغّل هذا الكود (code) مع `cargo run` وحمّل _127.0.0.1:7878_ في متصفحك (browser)؛ يجب أن ترى HTML الخاص بك معروضًا!

حاليًا، نحن نتجاهل بيانات (data) الطلب (request) في `http_request` ونرسل فقط محتويات ملف (file) HTML بشكل غير مشروط. وهذا يعني أنه إذا حاولت طلب (requesting) _127.0.0.1:7878/something-else_ في متصفحك (browser)، فستظل تحصل على نفس استجابة (response) HTML هذه. في الوقت الحالي، خادومنا (server) محدود جدًا ولا يقوم بما تفعله معظم خوادم الويب (web servers). نريد تخصيص استجاباتنا (responses) حسب الطلب وإرسال ملف HTML فقط لطلب صحيح إلى _/_.

### التحقق من الطلب والاستجابة بشكل انتقائي (Validating the Request and Selectively Responding)

الآن، سيُرجع خادوم الويب (web server) الخاص بنا HTML في الملف (file) بغض النظر عما طلبه العميل (client). لنضف الوظيفة (functionality) للتحقق من أن المتصفح (browser) يطلب _/_ قبل إرجاع ملف HTML وإرجاع خطأ إذا طلب المتصفح أي شيء آخر. لهذا نحتاج إلى تعديل `handle_connection`، كما هو موضح في القائمة (Listing) 21-6. يتحقق هذا الكود (code) الجديد من محتوى الطلب (request) المستلم مقابل ما نعرفه عن شكل طلب لـ _/_ ويضيف كتل (blocks) `if` و `else` لمعاملة الطلبات (requests) بشكل مختلف.

<Listing number="21-6" file-name="src/main.rs" caption="معالجة الطلبات (requests) إلى */* بشكل مختلف عن الطلبات الأخرى">

```rust,no_run
{{#rustdoc_include ../listings/ch21-web-server/listing-21-06/src/main.rs:here}}
```

</Listing>

سننظر فقط إلى السطر الأول من طلب (request) HTTP، لذا بدلاً من قراءة الطلب بالكامل في متجه (vector)، نستدعي `next` للحصول على العنصر الأول من المكرر (iterator). يعتني أول `unwrap` بـ `Option` ويوقف البرنامج إذا لم يكن للمكرر أي عناصر. يتعامل `unwrap` الثاني مع `Result` وله نفس التأثير مثل `unwrap` الذي كان في `map` المضاف في القائمة (Listing) 21-2.

بعد ذلك، نتحقق من `request_line` لنرى ما إذا كان يساوي سطر الطلب (request line) لطلب (request) GET إلى مسار (path) _/_. إذا كان الأمر كذلك، تُرجع كتلة (block) `if` محتويات ملف (file) HTML الخاص بنا.

إذا لم يساوِ `request_line` طلب (request) GET إلى مسار (path) _/_، فهذا يعني أننا تلقينا طلبًا آخر. سنضيف كودًا (code) إلى كتلة (block) `else` في لحظة للاستجابة لجميع الطلبات (requests) الأخرى.

شغّل هذا الكود (code) الآن واطلب (request) _127.0.0.1:7878_؛ يجب أن تحصل على HTML في _hello.html_. إذا قدمت أي طلب آخر، مثل _127.0.0.1:7878/something-else_، فستحصل على خطأ اتصال (connection error) مثل تلك التي رأيتها عند تشغيل الكود في القائمة (Listing) 21-1 والقائمة 21-2.

الآن لنضف الكود (code) في القائمة (Listing) 21-7 إلى كتلة (block) `else` لإرجاع استجابة (response) برمز حالة (status code) 404، الذي يشير إلى عدم العثور على المحتوى للطلب (request). سنُرجع أيضًا بعض HTML لصفحة لعرضها في المتصفح (browser) لتشير إلى الاستجابة للمستخدم النهائي.

<Listing number="21-7" file-name="src/main.rs" caption="الاستجابة برمز الحالة (status code) 404 وصفحة خطأ إذا تم طلب أي شيء غير */*">

```rust,no_run
{{#rustdoc_include ../listings/ch21-web-server/listing-21-07/src/main.rs:here}}
```

</Listing>

هنا، استجابتنا (response) لها سطر حالة (status line) برمز حالة (status code) 404 وعبارة السبب (reason phrase) `NOT FOUND`. سيكون جسم (body) الاستجابة هو HTML في الملف (file) _404.html_. ستحتاج إلى إنشاء ملف _404.html_ بجوار _hello.html_ لصفحة الخطأ؛ مرة أخرى، لا تتردد في استخدام أي HTML تريده، أو استخدم مثال HTML في القائمة (Listing) 21-8.

<Listing number="21-8" file-name="404.html" caption="محتوى نموذجي للصفحة لإرسالها مع أي استجابة (response) 404">

```html
{{#include ../listings/ch21-web-server/listing-21-07/404.html}}
```

</Listing>

مع هذه التغييرات، شغّل خادومك (server) مرة أخرى. طلب (requesting) _127.0.0.1:7878_ يجب أن يُرجع محتويات _hello.html_، وأي طلب (request) آخر، مثل _127.0.0.1:7878/foo_، يجب أن يُرجع خطأ HTML من _404.html_.

<!-- Old headings. Do not remove or links may break. -->

<a id="a-touch-of-refactoring"></a>

### إعادة الهيكلة (A Touch of Refactoring)

في الوقت الحالي، كتل (blocks) `if` و `else` لديها الكثير من التكرار: كلاهما يقرأ الملفات (files) ويكتب محتويات الملفات إلى التدفق (stream). الاختلافات الوحيدة هي سطر الحالة (status line) واسم الملف (filename). لنجعل الكود (code) أكثر إيجازًا عن طريق استخراج هذه الاختلافات في أسطر `if` و `else` منفصلة ستعيّن قيم سطر الحالة واسم الملف إلى المتغيرات (variables)؛ يمكننا بعد ذلك استخدام تلك المتغيرات بشكل غير مشروط في الكود لقراءة الملف (file) وكتابة الاستجابة (response). تُظهر القائمة (Listing) 21-9 الكود الناتج بعد استبدال كتل `if` و `else` الكبيرة.

<Listing number="21-9" file-name="src/main.rs" caption="إعادة هيكلة كتل (blocks) `if` و `else` لتحتوي فقط على الكود (code) الذي يختلف بين الحالتين">

```rust,no_run
{{#rustdoc_include ../listings/ch21-web-server/listing-21-09/src/main.rs:here}}
```

</Listing>

الآن تُرجع كتل (blocks) `if` و `else` فقط القيم المناسبة لسطر الحالة (status line) واسم الملف (filename) في صفة (tuple)؛ ثم نستخدم destructuring لتعيين هاتين القيمتين إلى `status_line` و `filename` باستخدام نمط (pattern) في عبارة (statement) `let`، كما تمت مناقشته في الفصل 19.

الكود (code) المكرر سابقًا الآن خارج كتل (blocks) `if` و `else` ويستخدم متغيرات (variables) `status_line` و `filename`. هذا يجعل من الأسهل رؤية الفرق بين الحالتين، ويعني أن لدينا مكانًا واحدًا فقط لتحديث الكود إذا أردنا تغيير كيفية عمل قراءة الملف (file) وكتابة الاستجابة (response). سيكون سلوك الكود في القائمة (Listing) 21-9 هو نفسه كما في القائمة 21-7.

رائع! الآن لدينا خادوم ويب (web server) بسيط في حوالي 40 سطرًا من كود (code) Rust يستجيب لطلب (request) واحد بصفحة محتوى ويستجيب لجميع الطلبات (requests) الأخرى باستجابة (response) 404.

حاليًا، يعمل خادومنا (server) في خيط (thread) واحد، مما يعني أنه يمكنه خدمة طلب (request) واحد فقط في كل مرة. لنفحص كيف يمكن أن تكون هذه مشكلة عن طريق محاكاة بعض الطلبات (requests) البطيئة. ثم سنصلحها حتى يتمكن خادومنا من معالجة طلبات متعددة في وقت واحد.
