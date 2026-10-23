<?php
require __DIR__.'/bootstrap.php';
$page=is_string($_GET['page']??null)?$_GET['page']:'';
if($page==='health') { db()->query('SELECT 1'); header('Content-Type: application/json');echo json_encode(['status'=>'ok','database'=>'connected']);exit; }
$error='';$notice='';
if($_SERVER['REQUEST_METHOD']==='POST') {
    verify_csrf(); $action=(string)($_POST['action']??'');
    if($action==='login') {
        $name=trim((string)($_POST['username']??''));
        $s=db()->prepare('SELECT id,username,password_hash FROM users WHERE username=? AND role=?');$s->execute([$name,'admin']);$user=$s->fetch();
        if($user && password_verify((string)($_POST['password']??''),$user['password_hash'])) {
            session_regenerate_id(true);$_SESSION['user_id']=$user['id'];$_SESSION['username']=$user['username'];$_SESSION['csrf']=bin2hex(random_bytes(32));audit('login_success',['user_id'=>$user['id']]);redirect('/?page=admin');
        }
        http_response_code(401);$error='Tên đăng nhập hoặc mật khẩu chưa đúng.';audit('login_failed');$page='login';
    } elseif($action==='logout') { session_destroy();redirect('/');
    } elseif($action==='save') {
        admin_required();$id=(int)($_POST['id']??0);$title=trim((string)($_POST['title']??''));$description=trim((string)($_POST['description']??''));
        $category=(int)($_POST['category_id']??0);$prep=(int)($_POST['prep_minutes']??0);$cook=(int)($_POST['cook_minutes']??0);$servings=(int)($_POST['servings']??0);
        $difficulty=(string)($_POST['difficulty']??'');$illustration=(string)($_POST['illustration']??'pho');
        $ingredientLines=array_values(array_filter(array_map('trim',explode("\n",(string)($_POST['ingredients']??'')))));
        $stepLines=array_values(array_filter(array_map('trim',explode("\n",(string)($_POST['steps']??'')))));
        $validCategory=in_array($category,array_column(categories(),'id'));
        if($title===''||strlen($title)>255||$description===''||!$validCategory||$prep<0||$prep>600||$cook<0||$cook>600||$servings<1||$servings>50||!in_array($difficulty,['Dễ','Vừa','Khó'],true)||!$ingredientLines||!$stepLines||count($ingredientLines)>50||count($stepLines)>30) {
            http_response_code(422);$error='Hãy nhập tên, mô tả, danh mục, nguyên liệu và các bước hợp lệ. Khẩu phần từ 1–50 người; mỗi thời gian tối đa 600 phút.';$page='edit';
        } else {
            if(!in_array($illustration,['pho','banh-mi','com-rang','canh-chua','salad','che'],true))$illustration='pho';
            $pdo=db();$pdo->beginTransaction();
            $values=[$title,$description,$category,$prep,$cook,$servings,$difficulty,$illustration];
            if($id) {
                if(!recipe($id)){http_response_code(404);exit('Không tìm thấy công thức.');}
                $pdo->prepare('UPDATE recipes SET title=?,description=?,category_id=?,prep_minutes=?,cook_minutes=?,servings=?,difficulty=?,illustration=? WHERE id=?')->execute([...$values,$id]);
                $pdo->prepare('DELETE FROM ingredients WHERE recipe_id=?')->execute([$id]);$pdo->prepare('DELETE FROM steps WHERE recipe_id=?')->execute([$id]);
            } else {
                $pdo->prepare('INSERT INTO recipes(title,description,category_id,prep_minutes,cook_minutes,servings,difficulty,illustration) VALUES(?,?,?,?,?,?,?,?)')->execute($values);$id=(int)$pdo->lastInsertId();
            }
            $s=$pdo->prepare('INSERT INTO ingredients(recipe_id,name,position) VALUES(?,?,?)');foreach($ingredientLines as $i=>$line)$s->execute([$id,$line,$i+1]);
            $s=$pdo->prepare('INSERT INTO steps(recipe_id,instruction,position) VALUES(?,?,?)');foreach($stepLines as $i=>$line)$s->execute([$id,$line,$i+1]);
            $pdo->commit();audit('recipe_saved',['recipe_id'=>$id]);redirect('/?page=admin&saved=1');
        }
    } elseif($action==='archive') {
        admin_required();$id=(int)($_POST['id']??0);db()->prepare('UPDATE recipes SET is_deleted=1 WHERE id=?')->execute([$id]);audit('recipe_archived',['recipe_id'=>$id]);redirect('/?page=admin');
    } elseif($action==='restore') {
        admin_required();$id=(int)($_POST['id']??0);db()->prepare('UPDATE recipes SET is_deleted=0 WHERE id=?')->execute([$id]);audit('recipe_restored',['recipe_id'=>$id]);redirect('/?page=admin&archived=1');
    }
}
$selected=isset($_GET['recipe'])?(int)$_GET['recipe']:0;
$detail=$selected?recipe($selected):false;
if($selected&&!$detail){http_response_code(404);$page='notfound';}
if(in_array($page,['admin','edit'],true))admin_required();
$title=$detail?$detail['title']:'Công thức ngon cho bữa cơm nhà';
require __DIR__.'/header.php';
if($error)echo '<div class="alert" role="alert">'.e($error).'</div>';
if($detail): ?>
<a class="back" href="/">← Khám phá công thức</a>
<article class="detail-hero"><div><span class="eyebrow"><?=e($detail['category'])?></span><h1><?=e($detail['title'])?></h1><p class="lead"><?=e($detail['description'])?></p><div class="facts"><span>◷ <?=e($detail['prep_minutes']+$detail['cook_minutes'])?> phút</span><span>♧ <?=e($detail['servings'])?> người</span><span><?=e($detail['difficulty'])?></span></div><button class="button secondary" onclick="window.print()">In công thức</button></div><img src="<?=e(image_for($detail['illustration']))?>" alt="Minh họa <?=e($detail['title'])?>"></article>
<div class="recipe-body"><aside class="ingredients"><span class="eyebrow">CHUẨN BỊ</span><h2>Nguyên liệu</h2><p>Cho <?=e($detail['servings'])?> người · Sơ chế <?=e($detail['prep_minutes'])?> phút</p><?php foreach(items('ingredients',$selected) as $i):?><label><input type="checkbox"> <span><?=e($i['name'])?></span></label><?php endforeach;?></aside><section class="steps"><span class="eyebrow">VÀO BẾP</span><h2>Cách thực hiện</h2><?php foreach(items('steps',$selected) as $i):?><div class="step"><b><?=e($i['position'])?></b><p><?=e($i['instruction'])?></p></div><?php endforeach;?><p class="note">Nấu chín kỹ thực phẩm, dùng dụng cụ sạch và điều chỉnh gia vị theo khẩu vị.</p></section></div>
<?php elseif($page==='login'): ?>
<section class="login-panel"><span class="eyebrow">GÓC NGƯỜI CHIA SẺ</span><h1>Chào bạn trở lại</h1><p>Đăng nhập để chăm chút những công thức của bạn.</p><form method="post"><?php csrf_field();?><input type="hidden" name="action" value="login"><label>Tên đăng nhập<input name="username" autocomplete="username" required maxlength="80"></label><label>Mật khẩu<input type="password" name="password" autocomplete="current-password" required></label><button class="button" type="submit">Đăng nhập</button></form></section>
<?php elseif($page==='admin'):
$archived=isset($_GET['archived']);$s=db()->prepare('SELECT r.*,c.name category FROM recipes r JOIN categories c ON c.id=r.category_id WHERE r.is_deleted=? ORDER BY r.id DESC');$s->execute([$archived?1:0]);$rows=$s->fetchAll(); ?>
<section class="section-heading"><div><span class="eyebrow">QUẢN TRỊ RECIPE</span><h1>Góc bếp của bạn</h1><p>Xin chào <?=e($_SESSION['username'])?>. Quản lý món ăn, nguyên liệu và cách nấu tại đây.</p></div><a class="button" href="/?page=edit">+ Thêm công thức</a></section>
<?php if(isset($_GET['saved'])):?><p class="success">Đã lưu công thức thành công.</p><?php endif;?>
<div class="tabs"><a href="/?page=admin">Đang hiển thị</a><a href="/?page=admin&archived=1">Đã lưu trữ</a></div><div class="table-wrap"><table><thead><tr><th>Món ăn</th><th>Danh mục</th><th>Thời gian</th><th>Thao tác</th></tr></thead><tbody><?php foreach($rows as $r):?><tr><td><a href="/?recipe=<?=e($r['id'])?>"><?=e($r['title'])?></a></td><td><?=e($r['category'])?></td><td><?=e($r['prep_minutes']+$r['cook_minutes'])?> phút</td><td class="actions"><?php if(!$archived):?><a href="/?page=edit&id=<?=e($r['id'])?>">Sửa</a><?php endif;?><form method="post"><?php csrf_field();?><input type="hidden" name="action" value="<?=$archived?'restore':'archive'?>"><input type="hidden" name="id" value="<?=e($r['id'])?>"><button class="text-button" type="submit"><?=$archived?'Khôi phục':'Lưu trữ'?></button></form></td></tr><?php endforeach;?></tbody></table><?php if(!$rows):?><p class="empty">Chưa có công thức trong mục này.</p><?php endif;?></div>
<?php elseif($page==='edit'):
$id=(int)($_POST['id']??$_GET['id']??0);$r=$id?recipe($id):[];
if($id&&!$r){http_response_code(404);echo '<h1>Không tìm thấy công thức</h1>';}
else { $r=$r?:[]; if($_SERVER['REQUEST_METHOD']==='POST'&&$error)$r=array_merge($r,$_POST);
$ingredientText=$_POST['ingredients']??implode("\n",array_column($id?items('ingredients',$id):[],'name'));$stepText=$_POST['steps']??implode("\n",array_column($id?items('steps',$id):[],'instruction')); ?>
<a class="back" href="/?page=admin">← Về quản trị</a><h1><?=$id?'Chỉnh sửa':'Thêm'?> công thức</h1><form class="editor" method="post"><?php csrf_field();?><input type="hidden" name="action" value="save"><input type="hidden" name="id" value="<?=e($id)?>"><label>Tên món ăn<input name="title" value="<?=e($r['title']??'')?>" maxlength="120" required></label><label>Mô tả ngắn<textarea name="description" rows="3" required><?=e($r['description']??'')?></textarea></label><div class="form-grid"><label>Danh mục<select name="category_id"><?php foreach(categories() as $c):?><option value="<?=e($c['id'])?>" <?=($r['category_id']??0)==$c['id']?'selected':''?>><?=e($c['name'])?></option><?php endforeach;?></select></label><label>Độ khó<select name="difficulty"><?php foreach(['Dễ','Vừa','Khó'] as $d):?><option <?=($r['difficulty']??'Dễ')===$d?'selected':''?>><?=e($d)?></option><?php endforeach;?></select></label><label>Sơ chế phút<input type="number" min="0" max="600" name="prep_minutes" value="<?=e($r['prep_minutes']??10)?>" required></label><label>Nấu phút<input type="number" min="0" max="600" name="cook_minutes" value="<?=e($r['cook_minutes']??20)?>" required></label><label>Khẩu phần người<input type="number" min="1" max="50" name="servings" value="<?=e($r['servings']??2)?>" required></label><label>Hình minh họa<select name="illustration"><?php foreach(['pho'=>'Món nước','banh-mi'=>'Bánh mì','com-rang'=>'Cơm','canh-chua'=>'Canh','salad'=>'Rau củ','che'=>'Món ngọt'] as $v=>$label):?><option value="<?=e($v)?>" <?=($r['illustration']??'pho')===$v?'selected':''?>><?=e($label)?></option><?php endforeach;?></select></label></div><label>Nguyên liệu mỗi dòng một nguyên liệu<textarea name="ingredients" rows="8" required placeholder="300 g thịt gà&#10;1 củ hành tây"><?=e($ingredientText)?></textarea></label><label>Cách làm mỗi dòng một bước<textarea name="steps" rows="8" required><?=e($stepText)?></textarea></label><button class="button" type="submit">Lưu công thức</button></form>
<?php } elseif($page==='notfound'):?><section class="empty"><h1>Chưa tìm thấy món này</h1><p>Công thức có thể đã được lưu trữ.</p><a class="button" href="/">Về trang chủ</a></section>
<?php else:
$q=is_string($_GET['q']??null)?trim($_GET['q']):'';$category=(int)($_GET['category']??0);$params=[];$where='r.is_deleted=0';
if($q!==''){$where.=' AND (r.title LIKE ? OR r.description LIKE ? OR EXISTS(SELECT 1 FROM ingredients i WHERE i.recipe_id=r.id AND i.name LIKE ?))';$params=array_fill(0,3,'%'.$q.'%');}
if($category){$where.=' AND r.category_id=?';$params[]=$category;}
$s=db()->prepare('SELECT r.*,c.name category FROM recipes r JOIN categories c ON c.id=r.category_id WHERE '.$where.' ORDER BY r.id');$s->execute($params);$recipes=$s->fetchAll();$count=db()->query('SELECT COUNT(*) FROM recipes WHERE is_deleted=0')->fetchColumn(); ?>
<section class="hero"><div class="hero-copy"><span class="eyebrow"><span class="tiny-dot"></span> TỪ CĂN BẾP NHỎ</span><h1>Bữa ngon mỗi ngày,<br><em>ấm lòng mỗi nhà.</em></h1><p>Những công thức gần gũi, nguyên liệu dễ tìm.<br>Cùng vào bếp và giữ lại hương vị bạn yêu.</p><a class="button" href="#cong-thuc">Khám phá công thức <span>↗</span></a><div class="hero-proof"><span class="mini-chef">♧</span><div><b><?=e($count)?> công thức được chia sẻ</b><small>Nấu từng bước · Ngon theo cách của bạn</small></div></div></div><div class="hero-art"><img src="/assets/pho.svg" alt="Minh họa tô phở gà với rau thơm"><div class="floating-label"><span>◷</span><div><b>Hôm nay ăn gì?</b><small>Bắt đầu từ một tô phở nóng</small></div></div><span class="art-caption">MÓN VIỆT · BẾP NHÀ</span></div></section>
<section id="cong-thuc"><div class="section-heading"><div><span class="eyebrow">CẢM HỨNG VÀO BẾP</span><h2>Chọn món bạn thích</h2></div><form class="search" action="/#cong-thuc" method="get"><label class="sr-only" for="q">Tìm món ăn hoặc nguyên liệu</label><input id="q" name="q" value="<?=e($q)?>" placeholder="Tên món hoặc nguyên liệu…"><button type="submit" aria-label="Tìm công thức">⌕</button></form></div><nav class="filters" aria-label="Danh mục món ăn"><a class="<?=$category===0?'active':''?>" href="/?q=<?=e(urlencode($q))?>#cong-thuc">Tất cả</a><?php foreach(categories() as $c):?><a class="<?=$category===$c['id']?'active':''?>" href="/?category=<?=e($c['id'])?>&q=<?=e(urlencode($q))?>#cong-thuc"><?=e($c['name'])?></a><?php endforeach;?></nav><p class="result-count"><?=e(count($recipes))?> công thức<?=$q!==''?' cho “'.e($q).'”':''?></p><div class="cards"><?php foreach($recipes as $r):?><article class="card"><a class="card-image" href="/?recipe=<?=e($r['id'])?>"><img src="<?=e(image_for($r['illustration']))?>" alt="Minh họa <?=e($r['title'])?>"><span class="difficulty"><?=e($r['difficulty'])?></span></a><div class="card-body"><span class="eyebrow"><?=e($r['category'])?></span><h3><a href="/?recipe=<?=e($r['id'])?>"><?=e($r['title'])?></a></h3><p><?=e($r['description'])?></p><div class="card-meta"><span>◷ <?=e($r['prep_minutes']+$r['cook_minutes'])?> phút</span><span>♧ <?=e($r['servings'])?> người</span><a aria-label="Xem <?=e($r['title'])?>" href="/?recipe=<?=e($r['id'])?>">↗</a></div></div></article><?php endforeach;?></div><?php if(!$recipes):?><div class="empty"><h3>Chưa tìm thấy công thức phù hợp</h3><p>Thử một nguyên liệu khác hoặc xem tất cả món ăn.</p><a href="/">Xem tất cả</a></div><?php endif;?></section>
<section class="kitchen-note"><span>✳</span><div><h2>Một chút kiên nhẫn. Một bữa cơm ngon.</h2><p>Đọc kỹ công thức, chuẩn bị đủ nguyên liệu rồi cùng bắt đầu nhé.</p></div><a href="/?recipe=1">Thử món đầu tiên ↗</a></section>
<?php endif;require __DIR__.'/footer.php'; ?>
