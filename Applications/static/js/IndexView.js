document.addEventListener('DOMContentLoaded', () => {
    const indexHeader = document.getElementById("index-header");
    const indexPage = document.getElementById("index-page");
    const productPage = document.getElementById("product-page");
    const orderPage = document.getElementById("order-page");
    const reportPage = document.getElementById("report-page");

    const path = window.location.pathname;

    if (path === "/product") {
        if (indexHeader) indexHeader.style.display = "none";
        if (indexPage) indexPage.style.display = "none";
        if (productPage) productPage.style.display = "block";
    } else if (path === "/order") {
        if (indexHeader) indexHeader.style.display = "none";
        if (indexPage) indexPage.style.display = "none";
        if (orderPage) orderPage.style.display = "block";
    } else if (path === "/report") {
        if (indexHeader) indexHeader.style.display = "none";
        if (indexPage) indexPage.style.display = "none";
        if (reportPage) reportPage.style.display = "block";
    }
});