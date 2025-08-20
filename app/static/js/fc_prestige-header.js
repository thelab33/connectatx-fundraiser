addEventListener("fc:meter:update", () => {
  const f = document.querySelector("#hdr-meter .fill");
  if (f) {
    f.animate(
      [{ filter: "brightness(1.6)" }, { filter: "brightness(1)" }],
      { duration: 600, easing: "ease-out" }
    );
  }
});
