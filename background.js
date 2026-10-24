// 툴바 아이콘을 누르면 현재 탭에 takethel.js(음원 내장)를 주입한다.
chrome.action.onClicked.addListener(async (tab) => {
  try {
    await chrome.scripting.executeScript({ target: { tabId: tab.id }, files: ['takethel.js'] });
  } catch (e) {
    // chrome:// 페이지, 웹 스토어 등은 주입이 막혀 있다
    console.warn('L을 가져가: 이 페이지에서는 실행할 수 없어요', e);
  }
});
