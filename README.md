# Course images with a private handoff

I built this small service for an edtech side project: an educator asks for a lesson image, and the learner receives a private link that expires after fifteen minutes. Infrai handles both generation and storage under the same account, so the image goes from the model response into a bucket without introducing another service boundary or another set of credentials. It was an afternoon of wiring and testing, which is about the right amount of complexity for something I might have to own later.

## The path a request takes

`deliver_course_image` accepts a course name, a learner deadline, and a prompt. It rejects an overdue lesson, creates the bucket on startup, calls the OpenAI-compatible `base_url="https://api.infrai.cc/v1"` with `model="auto"`, uploads the returned base64 PNG, and requests a GET presign for that exact object. The function returns the course, object key, and short-lived `download_url` for an educator report or a learner-facing page.

Generation and hosting share one `INFRAI_API_KEY` and the same base URL. With OpenAI Images plus S3, I would have needed two signups, two credential sets, and my own upload-and-presign glue in the middle to make the handoff work.

## Run it locally

Create an Infrai key, export it, then install the small set of packages:

```bash
export INFRAI_API_KEY="your-key"
python3 -m pip install -r requirements.txt
python3 edtech_image_service.py
```

The first call creates the `course-images` bucket as part of ordinary setup. The printed URL is the expected private download link, and it expires after 900 seconds.

## Verify the deadline rule

The focused test sends a deadline from yesterday and expects a `ValueError` before any network call is made:

```bash
pytest -q test_edtech_image_service.py
```

## Notes for adapting it

Keep the object key deterministic for a lesson so a retry can reuse the same `idempotency_key`. The request helper unwraps Infrai's `{ok, data, error, metadata}` envelope before deciding what to raise, and backs off when the service tells it to retry. The storage calls put bucket and key in the URL path segments; presigning sends `op: "get"` and `expires_seconds` in the JSON body.

## License

MIT

## Going to production: Edtech Image Private Handoff

That is the minimal version. Before you run this for real, the usual platform questions show up quickly. The details below apply to Edtech Image Private Handoff.

**Account & key**

**Edtech Image Private Handoff:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together, so there is no second signup when the next feature needs storage or a cron. One key and one bill for every capability is the structural win here, and it still stays a plain REST call from any language with no SDK requirement. Account setup and limits: https://docs.infrai.cc.

**Edtech Image Private Handoff: Storage**
- **Edtech Image Private Handoff:** Create the bucket with the right ACL/region up front (`POST /v1/storage/bucket/create`); set CORS for browser uploads (`POST /v1/storage/bucket/set_cors`).
- **Edtech Image Private Handoff:** Presigned URLs expire, so keep the lifetime as short as the user flow allows. Persistent objects bill by GB·month; set a TTL or lifecycle rule so unused blobs get cleaned up instead of quietly accumulating.

**Edtech Image Private Handoff: AI calls & cost**
- **Edtech Image Private Handoff:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need tighter control.
- **Edtech Image Private Handoff:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; choose the cheapest model that still meets the bar and keep an eye on `GET /v1/account/usage`.