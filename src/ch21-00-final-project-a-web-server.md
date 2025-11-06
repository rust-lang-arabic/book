# المشروع النهائي: بناء خادوم ويب متعدد الخيوط (Final Project: Building a Multithreaded Web Server)

لقد كانت رحلة طويلة (long journey)، ولكننا وصلنا (we've reached) إلى نهاية الكتاب (end of the book). في هذا الفصل (In this chapter)، سنبني (we'll build) مشروعًا (project) آخر معًا (together) لنوضح (to demonstrate) بعض المفاهيم (some of the concepts) التي غطيناها (we covered) في الفصول الأخيرة (final chapters)، بالإضافة إلى (as well as) تلخيص (recap) بعض الدروس السابقة (some earlier lessons).

لمشروعنا النهائي (For our final project)، سنصنع (we'll make) خادوم ويب (web server) يقول (that says) "Hello!" ويبدو (and looks) مثل الشكل (like Figure) 21-1 في متصفح الويب (in a web browser).

فيما يلي (Here is) خطتنا (our plan) لبناء (for building) الخادوم (the web server):

1. تعلم (Learn) قليلاً (a bit) عن (about) TCP و (and) HTTP.
2. الاستماع (Listen) لاتصالات (for connections) TCP على مقبس (on a socket).
3. تحليل (Parse) عدد صغير (a small number) من طلبات (of requests) HTTP.
4. إنشاء (Create) استجابة (response) HTTP مناسبة (proper).
5. تحسين (Improve) الإنتاجية (the throughput) لخادومنا (of our server) باستخدام (with) مجمع خيوط (a thread pool).

<img alt="Screenshot of a web browser visiting the address 127.0.0.1:8080 displaying a webpage with the text content "Hello! Hi from Rust"" src="img/trpl21-01.png" class="center" style="width: 50%;" />

<span class="caption">الشكل (Figure) 21-1: مشروعنا النهائي المشترك (Our final shared project)</span>

قبل أن نبدأ (Before we get started)، يجب أن نذكر (we should mention) تفصيلتين (two details). أولاً (First)، الطريقة (the method) التي سنستخدمها (we'll use) لن تكون (won't be) أفضل طريقة (the best way) لبناء (to build) خادوم ويب (a web server) باستخدام (with) Rust. نشر (have published) أعضاء المجتمع (Community members) عددًا (a number) من الحزم (of crates) الجاهزة للإنتاج (production-ready) المتاحة (available) على (at) [crates.io](https://crates.io/) والتي توفر (that provide) تطبيقات (implementations) أكثر اكتمالاً (more complete) لخادوم الويب (web server) ومجمع الخيوط (and thread pool) مما سنبنيه (than we'll build). ومع ذلك (However)، فإن نيتنا (our intention) في هذا الفصل (in this chapter) هي مساعدتك (is to help you) على التعلم (learn)، وليس (not) اتخاذ الطريق السهل (to take the easy route). نظرًا لأن (Because) Rust هي لغة برمجة أنظمة (systems programming language)، يمكننا (we can) اختيار (choose) مستوى التجريد (the level of abstraction) الذي نريد (we want) العمل به (to work with) ويمكننا (and can) الذهاب (go) إلى مستوى أدنى (to a lower level) مما هو ممكن (than is possible) أو عملي (or practical) في لغات أخرى (in other languages).

ثانيًا (Second)، لن نستخدم (we will not be using) async و (and) await هنا (here). بناء (Building) مجمع خيوط (a thread pool) هو تحدٍ (is a challenge) كبير (big enough) بما فيه الكفاية (on its own) بمفرده، دون إضافة (without adding in) بناء (building) وقت تشغيل async (async runtime)! ومع ذلك (However)، سنلاحظ (we will note) كيف (how) يمكن أن تنطبق (might be applicable) async و (and) await على بعض المشاكل نفسها (to some of the same problems) التي سنراها (we will see) في هذا الفصل (in this chapter). في النهاية (Ultimately)، كما لاحظنا (as we noted) في الفصل (in Chapter) 17، تستخدم (use) العديد من (many) أوقات تشغيل async (async runtimes) مجمعات الخيوط (thread pools) لإدارة (for managing) عملها (their work).

لذلك (We'll therefore) سنكتب (write) خادوم (server) HTTP الأساسي (the basic) ومجمع الخيوط (and thread pool) يدويًا (manually) حتى (so that) تتمكن (you can) من تعلم (learn) الأفكار (the ideas) والتقنيات (and techniques) العامة (general) وراء (behind) الحزم (the crates) التي قد تستخدمها (you might use) في المستقبل (in the future).
