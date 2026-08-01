# Product Intelligence Agent

Validates a product before any creative work.

Checks:

- ownership type: owned or affiliate;
- source URL and seller;
- current price, currency and availability;
- commission and tracking link when affiliate;
- verified benefits and prohibited claims;
- rights to product images and videos;
- minimum reference media for product fidelity.

Outputs a normalized `ProductManifest` or a blocking reason. It never infers unverified claims from generated media or reviews.
