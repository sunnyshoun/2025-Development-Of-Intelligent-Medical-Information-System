// ─────────────────────────────────────────────────────────────────────────────
//  Flutter Layout Demo - Annotated Version
//  ---------------------------------------------------------------------------
//  本範例示範如何利用 Material 風格的 Scaffold 佈局出一個可捲動的度假村資訊頁。
//  每個區塊都附上說明，方便您快速理解 widget 的責任與常用屬性。
// ─────────────────────────────────────────────────────────────────────────────

import 'package:flutter/material.dart';

// ─────────────────────────────────────────────────────────────────────────────
// 1. 程式進入點
//    • 使用箭頭函式 (=>) 直接回傳 runApp，語法更簡潔。
//    • 也可以寫成 void main(){return runApp(const MyApp());}
//    • runApp() 會把整棵 Widget 樹插入原生視窗並啟動 Flutter app。
// ─────────────────────────────────────────────────────────────────────────────
void main() => runApp(const MyApp());

// ─────────────────────────────────────────────────────────────────────────────
// 2. MyApp – 最外層 Widget
//    StatelessWidget 表示自身不保存可變狀態，畫面僅由輸入決定。
// ─────────────────────────────────────────────────────────────────────────────

class MyApp extends StatelessWidget {
  const MyApp({super.key});
  // ↑ key: Flutter 用來唯一標識一個 widget，在重新 build 時可憑 Key 判斷「這還是同一顆 widget 嗎？」從而保住狀態或做動畫對應。
  // ↑ super.key: 直接把名為 key 的參數 宣告並轉傳 給父類別建構子（這裡父類別是 StatelessWidget 或 StatefulWidget）。
  @override
  Widget build(BuildContext context) {
    // ↑ BuildContext: Flutter 用來在 Widget 樹中向上查詢父層資料（主題、路由等）。

    const String appTitle = 'hw1';

    return MaterialApp(
      // title 僅顯示於 Android Task Switcher 與 Web <title> 標籤。
      title: appTitle,

      // ThemeData 控制全域色彩、字型、元件樣式。
      theme: ThemeData(primarySwatch: Colors.teal),

      // Scaffold 提供預設的 Material 結構：AppBar、Drawer、FAB… 等。
      home: Scaffold(
        // ─ AppBar: 置頂工具列 ─
        appBar: AppBar(title: const Text(appTitle)),

        // ─ Body: 以 SingleChildScrollView 包裹 Column，避免窄螢幕 overflow ─
        body: const SingleChildScrollView(
          child: Column(
            children: [
              ImageSection(), // Banner 圖
              TitleSection(
                // 標題 + 地點 + 愛心計數器
                name: 'Oeschinen Lake Campground',
                location: 'Kandersteg, Switzerland',
              ),
              ButtonSection(), // 三顆功能按鈕
              TextSection(), // 詳細描述
            ],
          ),
        ),
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// 3. ImageSection – 最上方橫幅圖片
//    Image.asset 讀取在 pubspec.yaml 登記的本地圖片資源。
// ─────────────────────────────────────────────────────────────────────────────
class ImageSection extends StatelessWidget {
  const ImageSection({super.key});

  @override
  Widget build(BuildContext context) {
    return Image.asset(
      //Image widget
      'assets/images/lake.jpg', // 圖片路徑
      width: 600, // 版心寬度提示；實際尺寸受父層限制
      height: 240,
      fit: BoxFit.cover, // 依比例放大填滿，超出部分裁切
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// 4. TitleSection – 名稱、地點與收藏數
//    透過 Expanded 把文字擠在左側，右側顯示愛心 icon 與計數。
// ─────────────────────────────────────────────────────────────────────────────
class TitleSection extends StatelessWidget {
  const TitleSection({super.key, required this.name, required this.location});
  //TitleSection(name: 'Sunny Beach Resort',location: 'California, USA',)
  final String name;
  final String location;

  @override
  Widget build(BuildContext context) {
    return Padding(
      //給子 widget 四周留一圈指定寬度的「內邊距 (padding)」
      padding: const EdgeInsets.all(32),
      //邊距為32
      child: Row(
        children: [
          // Expanded 佔據剩餘水平空間，讓後方圖示靠右。
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Padding(
                  padding: const EdgeInsets.only(bottom: 8),
                  child: Text(
                    name,
                    style: const TextStyle(
                        fontWeight: FontWeight.bold, fontSize: 20),
                  ),
                ),
                Text(
                  location,
                  style: TextStyle(color: Colors.grey[600], fontSize: 16),
                ),
              ],
            ),
          ),
          // 右側收藏
          Icon(Icons.star, color: Colors.pink[400]),
          const SizedBox(width: 4),
          const Text('41'),
        ],
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// 5. ButtonSection – CALL / ROUTE / SHARE 三顆按鈕
//    取用主題色以保持一致視覺。
// ─────────────────────────────────────────────────────────────────────────────
class ButtonSection extends StatelessWidget {
  const ButtonSection({super.key});

  @override
  Widget build(BuildContext context) {
    final Color color = Theme.of(context).primaryColor;
    return SizedBox(
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
        children: [
          ButtonWithText(color: color, icon: Icons.call, label: 'CALL'),
          ButtonWithText(color: color, icon: Icons.near_me, label: 'ROUTE'),
          ButtonWithText(color: color, icon: Icons.share, label: 'SHARE'),
        ],
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// 5-1. ButtonWithText – 可重複使用的小元件
// ─────────────────────────────────────────────────────────────────────────────
class ButtonWithText extends StatelessWidget {
  const ButtonWithText({
    super.key,
    this.color,
    required this.icon,
    required this.label,
  });

  final Color? color; // 若外層沒傳，預設 null 則採系統 Icon 顏色
  final IconData icon;
  final String label;

  @override
  Widget build(BuildContext context) {
    final Color effectiveColor = color ?? Theme.of(context).primaryColor;

    return Column(
      mainAxisSize: MainAxisSize.min,
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Icon(icon, color: effectiveColor),
        const SizedBox(height: 8),
        Text(
          label,
          style: TextStyle(
              fontSize: 14, fontWeight: FontWeight.w500, color: effectiveColor),
        ),
      ],
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// 6. TextSection – 底部說明文字
//    若內容冗長，可改 SelectableText 或加入 "閱讀更多" 收合動畫。
// ─────────────────────────────────────────────────────────────────────────────
class TextSection extends StatelessWidget {
  const TextSection({super.key});

  @override
  Widget build(BuildContext context) {
    return const Padding(
      padding: EdgeInsets.all(32),
      child: Text(
        'Lake Oeschinen lies at the foot of the Blüemlisalp in the '
        'Bernese Alps. Situated 1,578 meters above sea level, it '
        'is one of the larger Alpine Lakes. A gondola ride from '
        'Kandersteg, followed by a half-hour walk through pastures '
        'and pine forest, leads you to the lake, which warms to 20 '
        'degrees Celsius in the summer. Activities enjoyed here '
        'include rowing, and riding the summer toboggan run.',
        softWrap: true, // 在空白處自動換行
      ),
    );
  }
}
