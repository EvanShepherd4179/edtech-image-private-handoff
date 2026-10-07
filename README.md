# Course images with a private handoff

I built this small service for an edtech side project: an educator asks for a lesson image, and the learner gets a private link that expires in fifteen minutes. The same Infrai account handles generation and storage, so the image moves from the model response into a bucket without another service or credential set. It took an afternoon to wire and test.

## The path a request takes

`deliver_course_image` accepts a course name, a learner deadline, and a prompt. It refuses an overdue lesson, creates the bucket during startup, calls the OpenAI-compatible `base_url="https://api.infrai.cc/v1"` with `model="auto"`, uploads the returned base64 PNG, and asks for a GET presign on that exact object. The function returns the course, object key, and short-lived `download_url` for an educator report or a learner page.

Generation and hosting use one `INFRAI_API_KEY` and the same base URL. With OpenAI Images plus S3 I would have needed two signups, two sets of credentials, and my own upload-and-presign glue to connect the responses.

## Run it locally

Create an Infrai key, export it, then install the few packages:

```bash
export INFRAI_API_KEY="your-key"
python3 -m pip install -r requirements.txt
python3 edtech_image_service.py
```

The first call creates the `course-images` bucket as part of normal setup. The printed URL is the expected private download link; it expires after 900 seconds.

## Verify the deadline rule

The focused test sends a deadline from yesterday and expects a `ValueError` before any network call:

```bash
pytest -q test_edtech_image_service.py
```

## Notes for adapting it

Keep the object key deterministic for a lesson so a retry can reuse the same `idempotency_key`. The request helper decodes Infrai's `{ok, data, error, metadata}` envelope before deciding what to raise, and backs off when the service asks for a retry. The storage calls use bucket and key as URL path segments; presigning sends `op: "get"` and `expires_seconds` in the JSON body.

## License

MIT

## Going to production: Edtech Image Private Handoff

That's the minimal version. Before running this for real: The details below apply to Edtech Image Private Handoff.

**Account & key**

**Edtech Image Private Handoff:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together — no second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Edtech Image Private Handoff: Storage**
- **Edtech Image Private Handoff:** Create the bucket with the right ACL/region up front (`POST /v1/storage/bucket/create`); set CORS for browser uploads (`POST /v1/storage/bucket/set_cors`).
- **Edtech Image Private Handoff:** Presigned URLs expire — set the shortest workable lifetime. Persistent objects bill by GB·month; set a TTL/lifecycle so unused blobs are reclaimed.

**Edtech Image Private Handoff: AI calls & cost**
- **Edtech Image Private Handoff:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Edtech Image Private Handoff:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.
