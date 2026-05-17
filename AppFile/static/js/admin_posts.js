 // Pythonの辞書が、そのままJSのオブジェクト（連想配列）になる
const categoriesData = {{ categories_mapping | tojson }};

const groupSelect = document.getElementById('groupSelect');
const categorySelect = document.getElementById('categorySelect');

// グループの選択が変更（change）されたら発動
groupSelect.addEventListener('change', function()  {

    //選ばれたグループnoIDを取得(文字列として取得される)
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

const photoInput = document.getElementById("photo");
const removeButton = document.getElementById("remove-photo-button");

photoInput.addEventListener("change", function(){
    console.log("画像選択");
    //削除ボタン表示
    removeButton.hidden = false;
});
    
//削除ボタンを押した時
 removeButton.addEventListener("click", function(){

     photoInput.value = "";
     //削除ボタンを非表示
    removeButton.hidden =true;

    console.log("画像削除");

});