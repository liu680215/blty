var gulp = require('gulp');//自动化处理插件
var cssnano = require('gulp-cssnano');//压缩css文件插件
var rename = require('gulp-rename');//重命名插件
var jsuglify = require('gulp-uglify');//压缩js文件插件
var concat = require('gulp-concat');//合并多个js文件插件

var cache = require('gulp-cache');//压缩图片插件之二
var imagemin = require('gulp-imagemin');//压缩图片插件之一

var bs = require('browser-sync').create();//浏览器自动刷新插件
var sass = require('gulp-sass');//把scss文件转化为css文件插件

var util=require('gulp-util');//把错误打印出来，不退出gulp
var sourcemaps=require('gulp-sourcemaps');//可以找到js原文件出错位置
//定义公共路径
var path = {
    'css':'./src/css/**/',
    'images':'./src/images/',
    'js':'./src/js/',
    'css_dist':'./dist/css/',
    'images_dist':'./dist/images/',
    'js_dist':'./dist/js/',
    'html':'./templates/**/'
};
//处理html文件任务
gulp.task('html',function () {
    gulp.src(path.html+"*.html")
        .pipe(bs.stream()) //自动刷新页面。这个很关键！
});
//建立处理css文件任务
gulp.task('css',function () {
    gulp.src(path.css+"*.scss") //指定处理的文件源
        .pipe(sass().on("error",sass.logError)) //如果发生错误，就把错误显示出来
        .pipe(cssnano()) //交给cssnano进行压缩
        .pipe(rename({"suffix":".min"})) //重新命名,该功能是在原有文件名后+min
        .pipe(gulp.dest(path.css_dist)) //把压缩的文件放到指定的目录
        .pipe(bs.stream()) //自动刷新页面。这个很关键！
});
//建立处理js文件任务
gulp.task('js',function () {
gulp.src(path.js+'*.js') //指定处理的文件源
    .pipe(sourcemaps.init()) //初始化
    .pipe(jsuglify().on("error",util.log))
    .pipe(rename({"suffix":".min"})) //重新命名,该功能是在原有文件名后+min
    .pipe(sourcemaps.write())
    .pipe(gulp.dest(path.js_dist)) //把压缩的文件放到指定的目录
    .pipe(bs.stream()) //自动刷新页面。这个很关键！
});
//处理图片任务
gulp.task('images',function () {
    gulp.src(path.images+"*.*")
        .pipe(cache(imagemin()))
        .pipe(gulp.dest(path.images_dist))
        .pipe(bs.stream()) //自动刷新页面。这个很关键！
});
//定义监听文件修改任务
gulp.task('watch',function () {
     gulp.watch(path.html+"*.html",['html']);
    gulp.watch(path.css+"*.scss",['css']);
    gulp.watch(path.images+"*.*",['images']);
    gulp.watch(path.js+"*.js",['js']);
});
//建立任务初始化服务地址
gulp.task('bs',function () {
    bs.init({
        'server':{
            'baseDir':'./'
        }
    })
});
//建立一个默认任务
//gulp.task('default',['bs','watch']);
gulp.task('default',['watch']);