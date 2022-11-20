const roomName = JSON.parse(document.getElementById('room-name').textContent);

const prompt = document.querySelector("#prompt");
const category = document.querySelector("#category");

const emojiCollapse = document.getElementById('emojiCollapse');

const winnerModal = new bootstrap.Modal(document.getElementById('winnerModal'), {});
const winnerModalText = document.getElementById('winnerModalText');

const chatLog = document.querySelector('#chat-log');

const chatMembersText = {};
const chatMemberDisplay = document.querySelector('#chat-members');

let numMembers = Object.keys(chatMembersText).length;
let numUpdateRequests = 0;

const chatModeSwitch = document.querySelector('#chat-mode-switch');
const chatModeLabel = document.querySelector('#chat-mode-label');

const newRoundRequests = document.querySelector('#new-round-requests');

const emojiClueInput = document.querySelector("#emoji-clue-input");

const leaderDisplay = document.querySelector("#leader");
const currentRoundDisplay = document.querySelector("#current-round");

const promptContainer = document.querySelector("#row-5-wrapper");

const chatMessageInput = document.querySelector('#chat-message-input');

const chatMessageSubmit = document.querySelector('#chat-message-submit');

const emojiPicker = document.querySelector('emoji-picker');

const copyRoomName = document.querySelector("#copy-input");

// AJAX requests
async function newPrompt() {
    var call = $.ajax({
        dataType: "json",
        url: `/chat/new_prompt/${roomName}/`,
        data: {username: userName},
    });

    //Listening to completion
    call.done(function(data){
        if (Object.hasOwn(data, 'error')) {
            console.log(data.error);
        } else {
            prompt.textContent = `"${data.updated_prompt}"`;
            category.textContent = data.updated_category;
            broadcastNewCategory(data.updated_category);
        }

    });
}

// Websocket Connection
const chatSocket = new WebSocket(
    'ws://'
    + window.location.host
    + '/ws/chat/'
    + roomName
    + '/'
    + userName
    + '/'
);
chatSocket.onclose = function(e) {
    console.error('Chat socket closed unexpectedly');
    window.location = '/chat/';
    // TODO: Send request to backend, to delete RoomMember object, and clean up room if empty.
    // TODO: Research sending task directly to off-prem queue, so cleanup happens even if server goes down.
};

// Websocket Receiver
chatSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    // populate chat messages
    if (Object.hasOwn(data, 'message')) {
        chatLog.innerHTML += formatChatMessage(data.user_emoji, data.username, data.message);
        chatLog.scrollTop = chatLog.scrollHeight;
    }

    // update last affirmation timestamp in chatMembersText Object
    if (Object.hasOwn(data, 'username')) {
        chatMembersText[data.username] = [ Date.now(), data.user_emoji ];
    }

    // evict old entries from chatMembersText
    now = Date.now();
    for (const [key, [timestamp, aliasEmoji]] of Object.entries(chatMembersText)) {
        diff = (now - timestamp) / 1000;
        if (diff > 2) {
            // Remove key from chatMembersText
            delete chatMembersText[key];
        }
    }

    // display chatMembersText
    let memberString = "";
    for (const aliasKey in chatMembersText) {
        [timestamp, aliasEmoji] = chatMembersText[aliasKey];
        if (aliasKey === userName) {
            memberString += "<label>" + aliasEmoji + aliasKey + "</label><br>";
        } else {
            memberString += "<text>" +aliasEmoji + aliasKey + "</text><br>";
        }
    }
    chatMemberDisplay.innerHTML = memberString;

    // Count requests until new round
    let numMembers = Object.keys(chatMembersText).length;
    if (Object.hasOwn(data, 'round_requests_update')) {
        numUpdateRequests = data.round_requests_update;
    }
    newRoundRequests.innerText = Math.floor(numMembers/2) + 1 - numUpdateRequests;

    // update emoji clue
    if (Object.hasOwn(data, 'update_emoji_clue')) {
        emojiClueInput.value = data['update_emoji_clue'];
    }

    // Start next round
    if (Object.hasOwn(data, 'start_next_round')) {
        leader = data['leader'];
        nextRound = data['start_next_round'];

        leaderDisplay.textContent = leader;
        currentRoundDisplay.textContent = nextRound;

        winnerModalText.textContent = leader;
        winnerModal.show();

        emojiClueInput.value = "";
        if (userName === leader) {
            emojiClueInput.disabled = false;
            promptContainer.hidden = false;
        } else {
            emojiClueInput.disabled = true;
            promptContainer.hidden = true;
        }
        prompt.textContent = "";

    }

    // Update category
    if (Object.hasOwn(data, 'new_category')) {
        category.textContent = data.new_category;
    }

};

// Websocket Send Functions
function broadcastEmojiClueChange() {
    if (userName === leader) {
        clue = emojiClueInput.value;
        chatSocket.send(JSON.stringify({
            'username': userName,
            'user_emoji': userEmoji,
            'update_emoji_clue': cleanEmojiClueInput(clue)
        }));
    }
}

function broadcastEndOfRoundVote() {
    chatSocket.send(JSON.stringify({
        'start_new_round': userName
    }));
}

function broadcastNewCategory(category) {
    chatSocket.send(JSON.stringify({
        'new_category': category
    }));
}

// Set Interval for sending affirmation to consumer, who broadcasts it to all connections
const affirmConnectionInterval = setInterval(() => {
    chatSocket.send(JSON.stringify({
        'username': userName,
        'user_emoji': userEmoji
    }));
    broadcastEmojiClueChange();
}, 1000);


// User Interaction
function updateChatModeText() {
    if (chatModeSwitch.checked) {
        chatModeLabel.innerText = "Chat Mode";
    } else {
        chatModeLabel.innerText = "Guess Mode";
    }
}

function toggleEmojiInput() {
    const emojiInputIsOpen = emojiCollapse.attributes['aria-expanded'].value === 'true';
    const isLeader = userName === leader;
    const shouldToggleEmojiInput = (!isLeader && emojiInputIsOpen) || (isLeader && !emojiInputIsOpen);

    if (shouldToggleEmojiInput) {
        // Toggle the accordion
        var collapseElementList = [].slice.call(document.querySelectorAll('.collapse'))
        var collapseList = collapseElementList.map(function (collapseEl) {
          return new bootstrap.Collapse(collapseEl)
        })
    }
}

chatMessageInput.focus();
chatMessageInput.onkeyup = function(e) {
    if (e.keyCode === 13) {  // enter, return
        document.querySelector('#chat-message-submit').click();
    }
};

chatMessageSubmit.onclick = function(e) {
    const messageInputDom = document.querySelector('#chat-message-input');
    const messageText = messageInputDom.value;
    chatSocket.send(JSON.stringify({
        'message': messageText,
        'username': userName,
        'user_emoji': userEmoji,
        'chat_mode': chatModeSwitch.checked  // false === guess mode, so actively process guesses
    }));
    messageInputDom.value = '';
};

emojiPicker.addEventListener('emoji-click', event => {
    if (userName === leader) {
        lastPos = insertAtCursor(emojiClueInput, event.detail.unicode);
        emojiClueInput.focus();
        emojiClueInput.selectionStart = lastPos;
        emojiClueInput.selectionEnd = lastPos;
        broadcastEmojiClueChange();
    }
  });

function copyLink() {
    // navigator clipboard api needs a secure context (https)
    copyRoomName.select();
    copyRoomName.setSelectionRange(0, 99999); // For mobile device
    if (navigator.clipboard && window.isSecureContext) {
        // navigator clipboard api method'
        return navigator.clipboard.writeText(copyRoomName.value);
    } else {
        // text area method
        let tempTextArea = document.createElement("tempTextArea");
        tempTextArea.value = copyRoomName.value;
        // make the textarea out of viewport
        tempTextArea.style.position = "fixed";
        tempTextArea.style.left = "-999999px";
        tempTextArea.style.top = "-999999px";
        document.body.appendChild(tempTextArea);
        // tempTextArea.focus();
        // tempTextArea.select();
        return new Promise((res, rej) => {
            document.execCommand('copy') ? res() : rej();
            tempTextArea.remove();
        });
    }
}

function expandLinkText() {
    copyRoomName.value =  `${domain}/chat/room/${roomName}`;
}
function shortenLinkText() {
    copyRoomName.value =  `.../chat/room/${roomName}`;
}

// Prevent keyboard input on emoji-clue-input, except for arrow keys and backspace
const allowedKeys = new Set([
    "Backspace",
    "ArrowLeft",
    "ArrowRight",
    "ArrowUp",
    "ArrowDown",
    "Tab",
    "Delete",
    "Shift",
    "Enter",
    " ",
]);
function preventKeyboardInput(event) {
    console.log(event);
    if (!(allowedKeys.has(event["key"]))) {
        event.preventDefault();
    }
}


// Utilities/Styling
function insertAtCursor(myField, myValue) {
    var startPos = myField.selectionStart;
    var endPos = myField.selectionEnd;
    var prevLen = myField.value.length;
    //IE support
    if (document.selection) {
        myField.focus();
        sel = document.selection.createRange();
        sel.text = myValue;
    }
    //MOZILLA and others
    else if (myField.selectionStart || myField.selectionStart === 0) {

        myField.value = myField.value.substring(0, startPos)
            + myValue
            + myField.value.substring(endPos, prevLen);
    } else {
        myField.value += myValue;
    }
    var shiftLen = (myField.value.length - prevLen);
    return endPos + shiftLen;
}

function htmlEncode(str) {
    return str.replace(/[\u00A0-\u9999<>\&]/g, function(i) {
       return '&#'+i.charCodeAt(0)+';';
    });
}
function formatChatMessage(userEmoji, userName, messageText) {
    messageText = htmlEncode(messageText);
    if (!chatModeSwitch.checked) {
        messageText = `<i><text style="color: #4ccf94;">${messageText}</text></i>`;
    }
    return `<text><b><text>${userEmoji}${userName}:</text></b>  ${messageText}</text><br>`;
}

// Clean the emoji-clue-input
const regExpEmoji = /(\s|\uD83E\uDD0F|\u2B55|[\u2700-\u27BF]|[\uE000-\uF8FF]|\uD83C[\uDC00-\uDFFF]|\uD83D[\uDC00-\uDFFF]|[\u2011-\u26FF]|\uD83E[\uDD10-\uDDFF]|[1-9]\uFE0F)/g;
const cleanEmojiClueInput = (value) => {
    emojiArray = [...value.matchAll(regExpEmoji)];
    emojis = emojiArray.map(item => item[0]).join("");
    return emojis;
}

// Keep chatMembers height in line with chatLog height, which is resizable by the user
function resizeChatMembers() {
    chatMemberDisplay.style.height = `${chatLog.offsetHeight}px`;
}
resizeChatMembers()
new ResizeObserver(resizeChatMembers).observe(chatLog);
