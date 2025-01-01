#include <bits/stdc++.h>
#define f(i,x,n,y) for(ll i=x;i<=n;i+=y)
#define f2(i,n,x,y) for(ll i=n;i>=x;i-=y)
#define ll long long
#define task "D"

using namespace std;
ll n,t,pre[100009],a[100009];
vector<ll> s;
struct node {ll cnt,ma;};

node tree[4000009];

void build (ll id,ll l,ll r,ll x,ll val)
{  
 if(l==r){
  tree[id].ma=val;
  tree[id].cnt=0;}
 else 
  {
    ll mid=(l+r)/2;
    if(mid>=x)
     build(id*2,l,mid,x,val);
    else 
     build(id*2+1,mid+1,r,x,val);
    tree[id].ma=max(tree[id*2].ma,tree[id*2+1].ma);  
  }
}

void update (ll id,ll l,ll r,ll u,ll v,ll val)
{
 
 if(l>v||r<u||l>r)
  return; 
 if(l>=u&&r<=v&&l<=r)
  {
   if(tree[id].ma<=val){
    tree[id].cnt++;
    return;}
 }
 else{
 ll mid=(l+r)/2; 
 update(id*2,l,mid,u,v,val);
 update(id*2+1,mid+1,r,u,v,val);}
 tree[id].cnt=tree[id*2].cnt+tree[id*2+1].cnt;    
}

ll get (ll id,ll l,ll r,ll u,ll v)
{
 if(l>v||r<u||l>r)
  return 0;
 if(l>=u&&r<=v)
  return tree[id].cnt;
 ll mid=(l+r)/2;
 return get(id*2,l,mid,u,v)+get(id*2+1,mid+1,r,u,v);      
}

ll pos (ll x)
{
 return lower_bound(s.begin(),s.end(),x)-s.begin()+1;
}


void solve ()
{
 cin>>n;
 f(i,1,n,1){
  ll x;
  cin>>x;
  pre[i]=pre[i-1]+x;
  s.push_back(pre[i]);
  }
 s.push_back(0); 
 sort(s.begin(),s.end());
 s.resize(distance(s.begin(),unique(s.begin(),s.end())));
 pre[0]=0;
 f(i,0,n,1){
  pre[i]=pos(pre[i]);
  a[i+1]=pre[i];
  build(1,1,n+1,i,a[i]);}

 //cout<<tree[5].ma<<" "<<tree[5].cnt<<'\n';
 //cout<<tree[10].ma<<'\n'; 
 f(i,2,n+1,1){
   update(1,1,n+1,1,i-1,a[i]);}
 //cout<<tree[10].ma<<" "<<tree[10].cnt<<'\n';       
 cout<<get(1,1,n+1,1,n+1)<<'\n'; 
 cout<<tree[4].ma<<" "<<tree[4].cnt; 
}

int main()
{
 ios_base::sync_with_stdio(false);
 cin.tie(NULL);cout.tie(NULL);
 if(fopen(task".INP", "r")) {
  freopen(task".INP", "r", stdin);
  freopen(task".OUT", "w", stdout);
 }
 t=1;
 while(t--)
  solve();
 return 0;
}
for i to n
  ans += get(1, pos(pre[i])) pos(pre[i]) la vi tri cua pre sau khi nen 
  update(pre) len segtree
dang bai la update 1 diem va get 1 doan