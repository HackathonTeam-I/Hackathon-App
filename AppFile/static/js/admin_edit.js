// Pythonの辞書が、そのままJSのオブジェクト（連想配列）になる
const categoriesData = {{ categories_mapping | tojson }};

const groupSelect = document.getElementById('groupSelect');
const categorySelect = document.getElementById('categorySelect');

// グループの選択が変更（change）されたら発動
groupSelect.addEventListener('change', function()  {

    //選ばれたグループのIDを取得(文字列として取得される)
     const selectedGroupId = this.value;

    //一旦カテゴリの選択肢を空っぽにする
    categorySelect.innerHTML = '<option value="">カテゴリを選択してください</option>';

    if (selectedGroupId !== "") {
         //選ばれたグループIDに対応するカテゴリの配列を取り出す
        const matchingCategories = categoriesData[selectedGroupId];

        //取り出したカテゴリを１つずつ<option>タグにして追加していく
        if (matchingCategories) {
            matchingCategories.forEach(category => {
                const option = document.createElement('option');
                option.value = category.id;
                option.textContent = category.name;
                categorySelect.appendChild(option);
            });
        }

        //カテゴリのプルダウンを操作可能（有効化）にする
        categorySelect.disabled = false;
    } else {
            //「選択してください」に戻された場合は、再び無効化する
            categorySelect.innerHTML = '<option value="">先にグループを選択してください</option>';
            categorySelect.disabled = true;
    }
});

//グループselectの初期値をセット
groupSelect.value = "{{ post.group_id }}";
//changeイベントを強制実行
groupSelect.dispatchEvent(new Event('change'));
//カテゴリの初期値をセット
categorySelect.value = "{{ post.category_id }}";
    

//写真投稿
const photoInput = document.getElementById("photo");
const removeButton = document.getElementById("remove-photo-button");
 const csrfToken = document.getElementById("csrf_token").value;

photoInput.addEventListener("change", function(){
    console.log("画像選択");
    //削除ボタン表示
    removeButton.hidden = false;
});
    

//削除ボタンがクリックされたらこの処理を実行する
removeButton.addEventListener("click", async function () {
    //HTMLのデータ属性を取得
    const postId = this.dataset.postId;
    const imageId = this.dataset.imageId;

    //通信失敗時にアプリが止まらないようにする
    try {
        //Flask API にアクセス(非同期通信)
        const response = await fetch(
             `/api/admin/posts/${postId}/images/${imageId}`,
             {
                method: "DELETE",
                //CSRF対策
                headers: {
                    "X-CSRFToken": csrfToken
                }
            }
        );
        //Flask が返した JSON を JavaScript のオブジェクトに変換
        const data = await response.json();

        if (response.ok) {

            alert(data.message);

            //画面から画像を消す
            document.querySelector(".current-image").remove();

        } else {
            //Flaskのメッセージを表示
            alert(data.message || "削除に失敗しました");

        }

    } catch (error) {

        console.error(error);
        //Flaskのメッセージを表示
        alert("通信エラーが発生しました");

    }

});