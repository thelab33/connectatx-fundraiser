document
  .querySelectorAll("img:not([fetchpriority=high]):not([loading])")
  .forEach((i) => {
    i.loading = "lazy";
    i.decoding = "async";
  });
