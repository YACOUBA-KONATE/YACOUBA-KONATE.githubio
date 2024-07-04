using Microsoft.EntityFrameworkCore;

namespace ProductionMVC.Models
{
	public class MVCDBCONTEXT : DbContext
	{
		public MVCDBCONTEXT(DbContextOptions options) : base(options)
		{
		}

		public DbSet<Production> Productions { get; set; }
		public DbSet<Category> Categories { get; set; }
	}
}
