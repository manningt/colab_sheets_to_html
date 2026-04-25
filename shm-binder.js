
// add an event listener to all images in the body
window.addEventListener('load', () => {
  document.body.addEventListener('click', (event) => {
    if (event.target.tagName === 'IMG') {
      // console.log('Image clicked via delegation:', event.target.src);
      myNewFunctionPopUp(event)
    }
  });
});

function myNewFunctionPopUp(event) {
  const figure = event.target.closest('figure');
  const caption = figure.querySelector('figcaption');
  // TODO: add check for bogus caption
  // if (caption) {
  //   console.log(caption.innerHTML);
  // }

  const bodyRect = document.body.getBoundingClientRect(); // gets the page size
  // console.log("bodyRect.left: " + bodyRect.left + " -- bodyRect.right: " + bodyRect.right);
  const elemRect = event.target.getBoundingClientRect();
  // console.log("elemRect.left: " + elemRect.left + " -- elemRect.right: " + elemRect.right);

  //calculate the left offset for the popup (left of the image, then position over the center of the image)
  const left = (elemRect.left - bodyRect.left) + (elemRect.right - elemRect.left) / 2; // finds the left offset for the popup (left of the image, then position over the center of the image)

  // finds the top for the popup (top of the image, and then a little bit from the popup height so it's above the image)
  const elemHeight = event.target.clientHeight;
  top = elemRect.top - bodyRect.top - (elemHeight / 1.5);

  var popup = document.getElementById("myPopup");
  popup.innerHTML = caption.innerHTML

  width = 360
  popup.style.width = width + "px";
  if (left + width > bodyRect.right) {
    popup.style.left = bodyRect.right - width + "px";
    //    console.log("set popup.style.left to: " + popup.style.left + " when left is: " + left + " bodyRight is:" + bodyRect.right);
  }
  else
    popup.style.left = left + "px";

  if (top < 10)
    popup.style.top = 10 + "px";
  else
    popup.style.top = top + "px";

  const dismissBtn = document.createElement("button");
  dismissBtn.innerHTML = "Dismiss";
  dismissBtn.className = "dismiss-btn"; // Add CSS classes for styling
  dismissBtn.addEventListener("click", function () {
    // popup.style.display = "none";
    // popup.remove()
    popup.classList.remove("show");
    // console.log("Dismiss button clicked")
  });
  popup.appendChild(dismissBtn);

  popup.classList.toggle("show");
}

/*
Calculating the popup window size:
iPhone SE portrait:
 screen width is 600, image width is 183

ipad portrait:
bodyRect.left: 0 -- bodyRect.right: 768
elemRect.left: 350 -- elemRect.right: 570

ipad landscape:
bodyRect.left: 0 -- bodyRect.right: 1024
elemRect.left: 387 -- elemRect.right: 607 -> width is 220

full screen:
bodyRect.left: 0 -- bodyRect.right: 1015
elemRect.left: 159 -- elemRect.right: 306 -> width is 147

if the left side of the image

*/