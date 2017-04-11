class PageInfo(object):

    def __init__(self, current_page, all_count, per_item=5):
        """
        :param current_page: 当前页
        :param all_count: 总文章数
        :param per_item: 每页显示数量
        """
        self.current_page = current_page
        self.all_count = all_count
        self.per_item = per_item

    @property
    def start(self):
        # 如果当前页大于从数据库中查的页数(传入页数有误)，那么当前页显示文章索引结束为下
        if self.current_page > self.all_page_count:
            return (self.all_page_count - 1) * self.per_item
        # 小于的话，从0开始
        elif self.current_page <= 0:
            return 0
        return (self.current_page - 1) * self.per_item

    @property
    def end(self):
        # 如果当前页大于从数据库中统计的总页数，那么当前页显示文章索引结束为下
        if self.current_page > self.all_page_count:
            return (self.all_page_count ) * self.per_item
        # 小于0的话，如下
        if self.current_page <= 0:
            return self.per_item
        return self.current_page * self.per_item

    @property
    def all_page_count(self):
        quotient, remainder = divmod(self.all_count, self.per_item)
        if remainder == 0:
            all_page_count = quotient
        else:
            all_page_count = quotient + 1
        return all_page_count

def Pager(page, all_page_count, murl):

    # 上一页
    page_html = []
    # if page > all_page_count:  # 超过最大页数后，点击上一页的url为最后一页
    #     home_html = '<li><a class="{0}" href="%s/%d.html">Home</a></li>' % (murl, 1)
    #     priv_html = '<li><a class="{0}" href="%s/%d.html">Previous page</a></li>' % (murl, all_page_count)
    #     page_html.append(home_html)
    #     page_html.append(priv_html)
    if page > 1:
        home_html = '<li><a class="{0}" href="%s/%d.html">Home</a></li>' % (murl, 1)
        priv_html = '<li><a class="{0}" href="%s/%d.html">Previous page</a></li>' % (murl, page-1)
        page_html.append(home_html)
        page_html.append(priv_html)


    # 当前页及中间的页
    for i in range(all_page_count):
        if page == i+1:  # i = 0 时，第一页
            present_html = '<li class="active"><a href="%s/%d.html">%d</a></li>' % (murl, i+1, i+1 )
        else: # 第二页到尾页
            present_html = '<li class=""><a href="%s/%d.html">%d</a></li>' % (murl, i+1, i+1 )
        page_html.append(present_html)

    # 下一页
    # if page < 1:  # 如果是负的页数，下一页显示第一页
    #     next_html = '<li><a class="{0}" href="%s/%d.html">Next page</a>' % (murl, 1)
    #     page_html.append(next_html)
    #     end_html = '<li><a class="{0}" href="%s/%d.html">End</a>' % (murl, all_page_count)
    #     page_html.append(end_html)
    if page < all_page_count:
        next_html = '<li><a class="{0}" href="%s/%d.html">Next page</a>' % (murl, page+1)
        page_html.append(next_html)
        end_html = '<li><a class="{0}" href="%s/%d.html">End</a>' % (murl, all_page_count)
        page_html.append(end_html)


    return page_html

if __name__ == '__main__':
    Pager(3, 10, 'sb')